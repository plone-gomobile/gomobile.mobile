"""
    Python implementation of ga.php.

    Orignal implementation: http://github.com/b1tr0t/Google-Analytics-for-Mobile--python-/blob/master/ga.py

    Some more info:

    * http://www.vdgraaf.info/google-analytics-without-javascript.html

    * http://www.vdgraaf.info/google-analytics-tweaks.html

    * http://svn.mobixx.net/svn/Branches/Exp/MetricsLogging/components/ContentAdaptationEngineEJB/src/main/java/com/siruna/contentadaptationengine/util/GoogleAnalytics.java

    * http://mobiforge.com/forum/running/analytics/google-analytics-mobile

    Adopted for Zope/Plone by mFabrik Research Oy.

    http://mfabrik.com



"""

import urllib
import re
try:
    from hashlib import md5
except ImportError:
    # py 2.4
    from md5 import md5

from random import randint
import struct
import httplib2
from httplib2 import HttpLib2Error
import time
import urlparse
from urllib import unquote, quote
from Cookie import SimpleCookie, CookieError
import uuid

from gomobile.mobile.utilities import get_ip

try:
    # The mod_python version is more efficient, so try importing it first.
    from mod_python.util import parse_qsl
except ImportError:
    from cgi import parse_qsl

import logging

logger = logging.getLogger("GAMobile")

VERSION = "4.4sh"
COOKIE_NAME = "__utmmobile"
COOKIE_PATH = "/"
COOKIE_USER_PERSISTENCE = 63072000

GIF_DATA = reduce(lambda x,y: x + struct.pack('B', y),
                  [0x47,0x49,0x46,0x38,0x39,0x61,
                   0x01,0x00,0x01,0x00,0x80,0x00,
                   0x00,0x00,0x00,0x00,0xff,0xff,
                   0xff,0x21,0xf9,0x04,0x01,0x00,
                   0x00,0x00,0x00,0x2c,0x00,0x00,
                   0x00,0x00,0x01,0x00,0x01,0x00,
                   0x00,0x02,0x01,0x44,0x00,0x3b], '')

# WHITE GIF:
# 47 49 46 38 39 61
# 01 00 01 00 80 ff
# 00 ff ff ff 00 00
# 00 2c 00 00 00 00
# 01 00 01 00 00 02
# 02 44 01 00 3b

# TRANSPARENT GIF:
# 47 49 46 38 39 61
# 01 00 01 00 80 00
# 00 00 00 00 ff ff
# ff 21 f9 04 01 00
# 00 00 00 2c 00 00
# 00 00 01 00 01 00
# 00 02 01 44 00 3b

def dbgMsg(msg):
    print msg
    logger.debug(msg)

def extract_ip(remote_address):
    # dbgMsg("remote_address: " + str(remote_address))
    if not remote_address:
        return ""
    matches = re.match('^([^.]+\.[^.]+\.[^.]+\.).*', remote_address)
    if matches:
        return matches.groups()[0] + "0"
    else:
        return ""

def get_visitor_id(guid, account, user_agent, cookie):
    """
     // Generate a visitor id for this hit.
     // If there is a visitor id in the cookie, use that, otherwise
     // use the guid if we have one, otherwise use a random number.
    """
    if cookie:
        return cookie
    else:
        return get_random_number()

    # does not understand the stuff b elow


    message = ""
    if guid:
        # Create the visitor id using the guid.
        message = guid + account
    else:
        # otherwise this is a new user, create a new random id.
        message = user_agent + str(uuid.uuid4())
    md5String = md5(message).hexdigest()
    return "0x" + md5String[:16]

def get_random_number():
    """
    // Get a random number string.
    """
    return str(randint(0, 0x7fffffff))

def write_gif_data():
    """
    // Writes the bytes of a 1x1 transparent gif into the response.

    Returns a dictionary with the following values:

    { 'response_code': '200 OK',
      'response_headers': [(Header_key, Header_value), ...]
      'response_body': 'binary data'
    }
    """
    response = {'response_code': '200 OK',
                'response_headers': [('Content-Type', 'image/gif'),
                                     ('Cache-Control', 'private, no-cache, no-cache=Set-Cookie, proxy-revalidate'),
                                     ('Pragma', 'no-cache'),
                                     ('Expires', 'Wed, 17 Sep 1975 21:32:10 GMT'),
                                     ],
                'response_body': GIF_DATA,
                }
    return response

def send_request_to_google_analytics(utm_url, environ):
    """
  // Make a tracking request to Google Analytics from this server.
  // Copies the headers from the original request to the new one.
  // If request containg utmdebug parameter, exceptions encountered
  // communicating with Google Analytics are thown.
    """
    http = httplib2.Http()
    try:
        resp, content = http.request(utm_url,
                                     "GET",
                                     headers={'User-Agent': environ.get('HTTP_USER_AGENT', 'Unknown'),
                                              'Accepts-Language:': environ.get("HTTP_ACCEPT_LANGUAGE",'')}
                                     )
        dbgMsg("GA call success:" + utm_url)

        return resp

    except HttpLib2Error, e:
        #errMsg("fail: %s" % utm_url)

        logger.error("GA URL failed:" + utm_url)

        if environ['GET'].get('utmdebug'):
            raise Exception("Error opening: %s" % utm_url)
        else:
            pass


def set_zope_cookie(response, cookie_name, value, expires, path):
    """ Set cookie, Zope way.

    @param cookie_name:

    @param expires:

    @param path: Path where cookie is effective
    """

    response.setCookie(cookie_name, value, expires=expires, path=path)

class BadTrackerId(Exception):
    pass


def xxx_track_page_view(request, response, environ, tracker_id, debug=False, synchronous=False):
    """ Make remote call / URL source to track a mobile visitors.

    @param tracker_id: String, MO-XXX something

    @param synchronous: If True use server-to-server tracking

    @return: URL to be used as image src or None if synchronous tracking is used
    """
    time_tup = time.localtime(time.time() + COOKIE_USER_PERSISTENCE)

    # set some useful items in environ:
    #environ['COOKIES'] = parse_cookie(environ.get('HTTP_COOKIE', ''))
    #environ['GET'] = {}
    #for key, value in parse_qsl(environ.get('QUERY_STRING', ''), True):
    #    environ['GET'][key] = value # we only have one value per key name, right? :)



    x_utmac = tracker_id #environ['GET'].get('x_utmac', None)

    #
    if not x_utmac.startswith("MO-"):
        raise BadTrackerId("Please use different tracking number for your mobile site than you normally use. Check from Google Analytics > site > check status > advanced settings > a site build for mobile phone. The number for is something like: MO-8819100-7")

    domain = environ.get('HTTP_HOST', '')

    # Get the referrer from the utmr parameter, this is the referrer to the
    # page that contains the tracking pixel, not the referrer for tracking
    # pixel.
    #document_referer = environ['GET'].get("utmr", "")
    document_referer = environ.get("HTTP_REFERER", None)
    if not document_referer or document_referer == "0":
        document_referer = "-"

    # http://www.teamrubber.com/blog/_serverrequest_uri-in-zope/

    # http://www.doughellmann.com/PyMOTW/urlparse/index.html

    full_url = request.ACTUAL_URL + "?" + request.QUERY_STRING
    parsed = urlparse.urlsplit(full_url)

    uri = parsed[2]
    if parsed[3]:
        uri += "?" + parsed[3]

    document_path = uri


    account = tracker_id
    user_agent = environ.get("HTTP_USER_AGENT", '')

    # Generate Google session cookie for the site

    # // Try and get visitor cookie from the request.
    cookie = request.cookies.get(COOKIE_NAME, None) #environ['COOKIES'].get(COOKIE_NAME)
    visitor_id = get_visitor_id(environ.get("HTTP_X_DCMGUID", ''), account, user_agent, cookie)

    # // Always try and add the cookie to the response.
    #cookie = SimpleCookie()
    #cookie[COOKIE_NAME] = visitor_id
    #morsel = cookie[COOKIE_NAME]
    #morsel['expires'] =
    #morsel['path'] = COOKIE_PATH

    # Extract client IP from the request
    ip = get_ip(request)

    expires = time.strftime('%a, %d-%b-%Y %H:%M:%S %Z', time_tup)
    set_zope_cookie(response, COOKIE_NAME, visitor_id, expires, COOKIE_PATH)

    utm_gif_location = "http://www.google-analytics.com/__utm.gif"


    # $urchinUrl='http://www.google-analytics.com/__utm.gif?
    # utmwv=1&
    # utmn='.$var_utmn.'&
    # utmsr='.$sr.'&
    # utmsc='.$sc.'&
    # utmul='.$ul.'&
    # utmje='.$je.'&
    # utmfl='.$fl.'&
    # utmdt='.$dt.'&
    # utmhn='.$var_utmhn.'&
    # utmr='.$var_referer.'&
    # utmp='.$var_utmp.'&
    # utmac='.$var_utmac.'&
    # utmcc=__utma%3D'.$var_cookie.'.'.$var_random.'.'.$var_today.'.'.$var_today.'.'.$var_today.'.2%3B%2B__utmb%3D'.$var_cookie.'%3B%2B__utmc%3D'.$var_cookie.'%3B%2B__utmz%3D'.$var_cookie.'.'.$var_today.'.2.2.utmccn%3D(direct)%7Cutmcsr%3D(direct)%7Cutmcmd%3D(none)%3B%2B__utmv%3D'.$var_cookie.'.'.$var_uservar.'%3B';

    #utmcc = '__utma%3D' + var_cookie '.' +
    #        var_random + '.$var_today.'.'.$var_today.'.'.$var_today.'.2%3B%2B__utmb%3D'.$var_cookie.'%3B%2B__utmc%3D'.$var_cookie.'%3B%2B__utmz%3D'.$var_cookie.'.'.$var_today.'.2.2.utmccn%3D(direct)%7Cutmcsr%3D(direct)%7Cutmcmd%3D(none)%3B%2B__utmv%3D'.$var_cookie.'.'.$var_uservar.'%3B'"


    var_random = get_random_number()
    var_cookie = visitor_id
    var_today = str(time.time())
    var_uservar = quote(user_agent)

    utmcc= '__utma%3D' + var_cookie+ '.' + var_random+ '.' + var_today+ '.' + var_today+ '.' + var_today + \
           '.2%3B%2B__utmb%3D' + var_cookie + '%3B%2B__utmc%3D' + var_cookie + '%3B%2B__utmz%3D' + \
            var_cookie+ '.' + var_today + '.2.2.utmccn%3D(direct)%7Cutmcsr%3D(direct)%7Cutmcmd%3D(none)%3B%2B__utmv%3D' + var_cookie+ '.' + var_uservar + '%3B';


    for utmac in [account, x_utmac]:
        if not utmac:
            continue # ignore empty utmacs
        # // Construct the gif hit url.
        utm_url = utm_gif_location + "?" + \
                "utmwv=" + VERSION + \
                "&utmac=" + utmac + \
                "&utmn=" + get_random_number() + \
                "&utmhn=" + quote(domain) + \
                "&utmr=" + quote(document_referer) + \
                "&utmp=" + quote(document_path) + \
                "&utmcc=" + utmcc + \
                "&utmvid=" + visitor_id

        if ip:

            # Mae IP to GA compatible format
            ip = extract_ip(ip)
            utm_url += "&utmip=" + ip

                #"&utmsr=" + environ['GET'].get('utmsr', '') + \
                #"&utme=" + environ['GET'].get('utme', '') + \


        if debug:
            # NOTE: Disabed as causes extra output during unit test run
            # dbgMsg("utm_url: " + utm_url)
            pass
        # Here you can turn on syncrhonous tracking...
        # disabled for now


    # // If the debug parameter is on, add a header to the response that contains
    # // the url that was used to contact Google Analytics.
    #headers = [('Set-Cookie', str(cookie).split(': ')[1])]

    if debug:
        response.setHeader('X-GA-MOBILE-URL', utm_url)

    if synchronous:
        # Call Analytics server-to-server
        response = send_request_to_google_analytics(utm_url, environ)
        return None
    else:
        # Create an image which calls GA

        # Must remain XHTML compatible
        utm_url = utm_url.replace("&", "&amp;")

        return utm_url


def track_page_view(request, response, environ, tracker_id, debug=False, synchronous=False):
    """ Make remote call / URL source to track a mobile visitors.

    @param tracker_id: String, MO-XXX something

    @param synchronous: If True use server-to-server tracking

    @return: URL to be used as image src or None if synchronous tracking is used
    """
    time_tup = time.localtime(time.time() + COOKIE_USER_PERSISTENCE)

    x_utmac = tracker_id #environ['GET'].get('x_utmac', None)

    if not x_utmac.startswith("MO-"):
        raise BadTrackerId("Please use different tracking number for your mobile site than you normally use. Check from Google Analytics > site > check status > advanced settings > a site build for mobile phone. The number for is something like: MO-8819100-7")

    domain = environ.get('HTTP_HOST', '')

    # Get the referrer from the utmr parameter, this is the referrer to the
    # page that contains the tracking pixel, not the referrer for tracking
    # pixel.
    document_referer = environ.get("HTTP_REFERER", None)
    if not document_referer or document_referer == "0":
        document_referer = "-"

    # http://www.teamrubber.com/blog/_serverrequest_uri-in-zope/
    # http://www.doughellmann.com/PyMOTW/urlparse/index.html
    full_url = request.ACTUAL_URL + "?" + request.QUERY_STRING
    parsed = urlparse.urlsplit(full_url)

    uri = parsed[2]
    if parsed[3]:
        uri += "?" + parsed[3]

    document_path = uri

    user_agent = environ.get("HTTP_USER_AGENT", '')

    # Generate Google session cookie for the site

    # // Try and get visitor cookie from the request.
    cookie = request.cookies.get(COOKIE_NAME, None) #environ['COOKIES'].get(COOKIE_NAME)
    visitor_id = get_visitor_id(environ.get("HTTP_X_DCMGUID", ''), tracker_id, user_agent, cookie)

    # // Always try and add the cookie to the response.
    #cookie = SimpleCookie()
    #cookie[COOKIE_NAME] = visitor_id
    #morsel = cookie[COOKIE_NAME]
    #morsel['expires'] =
    #morsel['path'] = COOKIE_PATH

    # Extract client IP from the request
    ip = get_ip(request)

    expires = time.strftime('%a, %d-%b-%Y %H:%M:%S %Z', time_tup)
    set_zope_cookie(response, COOKIE_NAME, visitor_id, expires, COOKIE_PATH)

    utm_gif_location = "http://www.google-analytics.com/__utm.gif"

    parameters = {
                  "utmac" : tracker_id,
                  "utmn" : get_random_number(),
                  "utmr" : document_referer,
                  "utmp" : document_path,
                  "guid" : "ON"
    }

    if ip:
        # Mae IP to GA compatible format
        ip = extract_ip(ip)
        # TODO: not sure if it works
        # parameters["utmip"] = ip

    # // Construct the gif hit url.
    utm_url = utm_gif_location + "?" + urllib.urlencode(parameters)

    if debug:
        response.setHeader('X-GA-MOBILE-URL', utm_url)

    if synchronous:
        # Call Analytics server-to-server
        response = send_request_to_google_analytics(utm_url, environ)
        return None
    else:
        # Create an image which calls GA

        # Must remain XHTML compatible
        utm_url = utm_url.replace("&", "&amp;")

        return utm_url

