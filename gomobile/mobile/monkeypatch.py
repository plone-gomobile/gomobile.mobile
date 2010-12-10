"""
    Python monkey patched code to make gomobile.mobile apply mobile
    theme when needed.

    http://mfabrik.com

"""

__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext"
__copyright__ = "2009-2010 mFabrik Research Oy"
__license__ = "GPL 2"

from base64 import encodestring
from urllib import quote
import urlparse
import logging


from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

#from layers import setMobileThemeLayer


from interfaces import MobileRequestType, IMobileRequestDiscriminator

logger = logging.getLogger("Plone")

#
# Monkey patch in the mobile support
#
# TODO do something smarter here
#
from Products.CMFCore.Skinnable import SkinnableObjectManager


# Don't mention anything about gomobile.mobile because
# this is rarely our cause... we just happen to be first
# code using components when HTTP request hits the server
BAD_RAP = """
    Zope start-up failed.
    Please start Zope in foreground mode or check logs to see which
    Python egg failed to load.
    """


def is_mobile(site, request):
    """ Special pre-traversing context discriminator

    @return: True if the request was a mobile site request
    """
    try:
        discriminator = getUtility(IMobileRequestDiscriminator)
    except ComponentLookupError:
        # This happens aaaalways....
        raise RuntimeError(BAD_RAP)

    # Determine mobile skin name from mobile_properties
    modes = discriminator.discriminate(site, request)
    # print "Discriminator:" + str(discriminator) + " modes:" + str(modes) + \
    #     " ids:" + str(properties.objectIds())
    #import pdb ; pdb.set_trace()
    return MobileRequestType.MOBILE in modes


def check_skin_exists(site, skin_name):
    """ Check that skin exists on the site and is usable.

    @param skin_name: Skin name as its on properties tab of portal_skins
    """
    portal_skins = site.portal_skins

    # ['Plone Default']
    available = portal_skins.getSkinSelections()
    return skin_name in available


def get_mobile_skin_name(site, request):
    """
    @return: Mobile theme name for a Plone site object
    """

    properties = site.portal_properties

    if hasattr(properties, "mobile_properties"):
        # Plone Mobile quickinstaller has been run
        # and we have mobile theme specifc files registeed

        mobile_properties = properties.mobile_properties

        # Enable mobile specific skin layer
        skin_name = mobile_properties.mobile_skin

        #print "Got skin:" + skin_name
        if not check_skin_exists(site, skin_name):

            if skin_name == "No Selection Made":
                # Uninstalled mobile theme marker string
                return None

            raise RuntimeError(
                "Current selected mobile theme %s is not installed on the "
                "site. Please install a mobile theme add-on using Add On "
                "installer in site setup." % skin_name)

        return skin_name
    else:
        # Happens when the site is still being constructed,
        # or when ZMI interface is accessed,
        # or on some views which do not travese Plone site.
        return None


def getSkinNameFromRequest(self, REQUEST=None):
    '''Returns the skin name from the Request.'''

    if REQUEST is None:
        return None
    sfn = self.getSkinsFolderName()

    if sfn is not None:

        sf = getattr(self, sfn, None)

        if is_mobile(self, REQUEST):

            skin = get_mobile_skin_name(self, REQUEST)
            if skin:
                return skin

        if sf is not None:
            return REQUEST.get(sf.getRequestVarname(), None)

SkinnableObjectManager.getSkinNameFromRequest = getSkinNameFromRequest


from Products.CMFCore.SkinsTool import SkinsTool


def getDefaultSkin(self):
    """ Get the default skin name.
    """
    site = self
    request = getattr(site, "REQUEST", None)
    if request:
        if is_mobile(site, request):
            return get_mobile_skin_name(site, request)

    return self.default_skin

SkinsTool.getDefaultSkin = getDefaultSkin

# Monkey patch authentication cookie (__ac)
# to support subdomains - otherwise mobile page and preview page
# requests require re auth
# Ugly but can't do otherwise
from Products.PluggableAuthService.plugins.CookieAuthHelper import \
    CookieAuthHelper


def getCookieDomain(request):
    """ Get a parent domain name to be used in the cookie

    One cookie covers all *.yoursite.com domains.
    """

    if "SERVER_URL" in request.environ:
        # WSGI based servers
        server_url = request.environ["SERVER_URL"]
    else:
        # Zope's Medusa
        server_url = request.other["SERVER_URL"]

    parts = urlparse.urlparse(server_url)
    netloc = parts[1]
    domain = netloc.split(":")[0]

    # Looks like at least Firefox does not allow set cookie domain ".localhost"
    # ugh
    # things gets ugly here

    # web.localhost -> localhost
    if "localhost" in domain:
        logger.warn("Mobilized Plone site must be configured to be accessed "
                    "using subdomains.")
        logger.warn("Otherwise preview and mobile site access.")
        logger.warn("Add following to your /etc/hosts:")
        logger.warn("127.0.0.1 mobi.site.foo web.site.foo preview.site.foo")
        logger.warn("..and access site site using fake domain name "
                    "web.site.foo.")
        logger.warn("Also DO NOT do Zope HTTP Basic Auth, since it is not "
                    "subdomain aware - use only Plone interface for login")
        logger.warn("See gomobile.mobile.monkeypatch for more info")

    if len(domain.split(".")) == 1:
        raise RuntimeError("You need to use subdomain to access the site. "
                           "E.g. web.localhost instead of localhost")

    domain_root = ".".join(domain.split(".")[1:])

    return "." + domain_root


def updateCredentials(self, request, response, login, new_password):
    """ Respond to change of credentials (NOOP for basic auth). """
    cookie_str = '%s:%s' % (login.encode('hex'), new_password.encode('hex'))
    cookie_val = encodestring(cookie_str)
    cookie_val = cookie_val.rstrip()

    domain = getCookieDomain(request)

    response.setCookie(self.cookie_name, quote(cookie_val), path='/',
                       domain=domain)


def resetCredentials(self, request, response):
    """ Raise unauthorized to tell browser to clear credentials. """
    domain = getCookieDomain(request)
    response.expireCookie(self.cookie_name, path='/', domain=domain)

CookieAuthHelper.resetCredentials = resetCredentials
