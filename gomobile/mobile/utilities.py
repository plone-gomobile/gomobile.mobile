"""

    Utility facilities to deal with mobile HTTP requests.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__author_url__ = "http://www.twinapex.com"

import urlparse

import re

import zope.interface
from zope import schema
from zope.component import getUtility, queryUtility
from zope.annotation import IAnnotations

from mobile.sniffer.utilities import get_user_agent
from mobile.heurestics.simple import is_low_end_phone

from Products.Five.browser import BrowserView
from gomobile.mobile.interfaces import IMobileUtility

from mfabrik.behaviorutilities.volatilecontext import AnnotationPersistentFactory, VolatileContext 

class MobileUtility(object):
    """ Zope 3 utility for mobile actions. 
    
    TODO: DONT USE. Get rid of this and use @@mobile_tool view.
    """

    zope.interface.implements(IMobileUtility)

    def isMobileRequest(self, request):
        """ Determine should this request be rendered in mobile mode. """

        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        if "HTTP_HOST" in request.environ:
            # Unit tests don't have HTTP_HOST
            if "mobi." in request.environ["HTTP_HOST"]:
                return True

        if self.isPreviewRequest(request):
            return True

        return False

    def isPreviewRequest(self, request):
        """ Determine should this request be rendered in mobile mode. """

        if "HTTP_HOST" in request.environ:
            if "preview." in request.environ["HTTP_HOST"]:
                return True

        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        return False

    def isLowEndPhone(self, request):
        """ @return True: If the user is visiting the site using a crappy mobile phone browser.

        Low end phones have problem with:

            - Complex HTML syntax

            - Several images on the same page

            - Advanced CSS styles

        Before using the techniques above please filter them away for the crappy phones.
        This concerns at least Nokia Series 40 phones.

        Note that Opera Mini browser works smoothly on low end phones too...
        """
        return is_low_end_phone(request)


def getMobileProperties(context, request):
    """ Cached access to mobile properties of the site.

    Will look up mobile properties from the database or return the cached instance.
    """
    return context.portal_properties.mobile_properties

# BBB
getCachedMobileProperties = getMobileProperties

def get_host(request):
    """ Helper function to extract host name from HTTP request in virtual host compatible way.
    
    """
    if "HTTP_X_FORWARDED_HOST" in request.environ:
        # Virtual host
        host = request.environ["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in request.environ:
        # Direct client request
        host = request.environ["HTTP_HOST"]
    else:
        # Unit test code?
        host = None
        
    return host

def get_host_domain_name(request):
    """
    Remove possible ports from HTTP host.
    """
    host = get_host(request)
    parts = host.split(":")
    return parts[0]
    
def get_ip(request):
    """  Extract the client IP address from the HTTP request in proxy compatible way.
    
    @return: IP address as a string or None if not available
    """
    if "HTTP_X_FORWARDED_FOR" in request.environ:
        # Virtual host
        ip = request.environ["HTTP_X_FORWARDED_FOR"]
    elif "REMOTE_ADDR" in request.environ:
        # Non-virtualhost
        ip = request.environ["REMOTE_ADDR"]
    else:
        # Unit test code?
        ip = None
        
    return ip
    
ipv4_regex_source = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
ipv4_regex = re.compile(ipv4_regex_source)

def is_numeric_ipv4(str):
    """
    
    http://answers.oreilly.com/topic/318-how-to-match-ipv4-addresses-with-regular-expressions/
        
    @param str: Hostname as a string.
    
    @return: True if the given string is numeric IPv4 address
    """
    # ^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
    return ipv4_regex.match(str)



    