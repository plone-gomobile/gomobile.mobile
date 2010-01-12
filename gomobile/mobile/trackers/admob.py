"""

    AdMob tracker - register at www.admob.com


    The orignal code courtesy of http://www.djangosnippets.org/snippets/883/

"""

from urllib2 import urlopen
from urllib import urlencode

try:
    # Python >= 2.5
    from hashlib import md5
except ImportError:
    # Python < 2.5
    from md5 import md5


import zope.interface

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileTracker

class AdmobTracker(object):
    """

    For tracking id, use your AdMob site id.

    Note: If ads are enabled on your AdMob acount will display ads and is not invisible.

    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId, debug):

        referer = self.request.get_header("referer", "")

        # TODO: This is virtual hostless path... strip site instance name here
        uri = self.request["PATH_TRANSLATED"]

        # Get Plone session id
        session_data_manager = getattr(self.context, "session_data_manager", None)

        if session_data_manager:
            session_id = session_data_manager.getBrowserIdManager().getBrowserId(create=create)
        else:
            # Unit tests
            session_id = "fake_session"

        params = {
          "admob_site_id" : trackingId,
        }

        html_code = admob_code(self.request, session_id, uri, params)

        return html_code

def admob_code(request, session, uri, admob_params=None):
    """ Plone/Zope specific AdMob code generator

    """
    # Change to "live" when ready to deploy.
    admob_mode = "test"

    admob_endpoint = "http://r.admob.com/ad_source.php"
    admob_version = "20080714-PYTHON"
    admob_timeout = 1.0
    admob_ignore = ("HTTP_PRAGMA", "HTTP_CACHE_CONTROL", "HTTP_CONNECTION", "HTTP_USER_AGENT", "HTTP_COOKIE",)

    # Build URL.
    admob_post = {}

    # Required Parameters - will raise if not found.
    admob_post["s"] = admob_params["admob_site_id"]

    # Meta Parameters.
    admob_post["u"] = request.get_header("HTTP_USER_AGENT", None)
    admob_post["i"] = request.get_header("REMOTE_ADDR", None)
    admob_post["p"] = uri
    admob_post["t"] = session

    # Hardcoded Parameters.
    admob_post["e"] = "UTF-8"
    admob_post["v"] = admob_version

    # Optional Parameters.
    admob_post["ma"] = admob_params.get("admob_markup", None)
    admob_post["d[pc]"] = admob_params.get("admob_postal_code", None)
    admob_post["d[ac]"] = admob_params.get("admob_area_code", None)
    admob_post["d[coord]"] = admob_params.get("admob_coordinates", None)
    admob_post["d[dob]"] = admob_params.get("admob_dob", None)
    admob_post["d[gender]"] = admob_params.get("admob_gender", None)
    admob_post["k"] = admob_params.get("admob_keywords", None)
    admob_post["search"] = admob_params.get("admob_search", None)

    for k, v in request.environ.items():
        if k not in admob_ignore:
            admob_post["h[%s]" % k] = v

    # Strip all ``None`` and empty values from admob_post.
    for k, v in admob_post.items():
        if v is None or v == "":
            admob_post.pop(k)

    if admob_mode == "test":
         admob_post["m"] = "test"

    # Request the Ad.
    admob_success = True
    try:
        admob_data = urlencode(admob_post)
        admob_file = urlopen(admob_endpoint, admob_data)
        admob_contents = admob_file.read()
        if admob_contents is None or admob_contents == "":
            admob_success = False
    except Exception, e:
        admob_success = False

    if not admob_success:
        admob_contents = "<img src=\"http://t.admob.com/li.php/c.gif/%(admob_site_id)s/1/%(admob_timeout)F/%(absolute_uri)s\" alt=\"\" width=\"1\" height=\"1\" />"  \
            % {"admob_site_id" : admob_params["admob_site_id"],
                 "admob_timeout" : admob_timeout,
                 "absolute_uri" : md5(uri).hexdigest()}

    # DEBUG:
    # print 'Connecting to: %s' % admob_endpoint
    # print 'Sending Parameters:'
    # print admob_post
    # print 'Got reponse:'
    # print admob_contents

    return admob_contents