"""
    Python monket patched code to make twinapex.plone.mobile work properly.
    
"""
from base64 import encodestring, decodestring
from urllib import quote, unquote
import urlparse
import logging

from zope.component import getUtility, queryUtility
from zope.component.interfaces import ComponentLookupError

from Products.CMFCore.Skinnable import SkinnableObjectManager
from Products.CMFCore.utils import getToolByName

from interfaces import MobileRequestType, IMobileRequestDiscriminator

logger = logging.getLogger("Plone")
#
# Monkey patch in the mobile support
#
# TODO do something smarter here
#
def getSkinNameFromRequest(self, REQUEST=None):
    '''Returns the skin name from the Request.'''

    if REQUEST is None:
        return None
    sfn = self.getSkinsFolderName()
    
    if sfn is not None:
       
        sf = getattr(self, sfn, None)
        
        properties = self.portal_properties

        try:
            discriminator = getUtility(IMobileRequestDiscriminator)
        except ComponentLookupError:
            # This happens aaaalways....
            raise RuntimeError("Cannot load IMobileRequestDiscriminator utility. This usually means that there has been error in your ZCML or Python modules imported by ZCML. Please see Zope start up logs.")
        
        site = self        

        # Determine mobile skin name from mobile_properties
        modes = discriminator.discriminate(site, REQUEST)
        
        if MobileRequestType.MOBILE in modes:
        
            if hasattr(sf, "mobile_base") and hasattr(properties, "mobile_properties"):
                # Plone Mobile quickinstaller has been run
                # and we have mobile theme specifc files registeed
                
                mobile_properties = properties.mobile_properties
                                                                
                # Enable mobile specific skin layer
                skin_name = mobile_properties.mobile_skin
                return skin_name
        
        if sf is not None:
            return REQUEST.get(sf.getRequestVarname(), None)

SkinnableObjectManager.getSkinNameFromRequest = getSkinNameFromRequest


# Monkey patch authentication cookie (__ac)
# to support subdomains - otherwise mobile page and preview page
# requests require re auth
# Ugly but can't do otherwise
from Products.PluggableAuthService.plugins.CookieAuthHelper import CookieAuthHelper

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
        logger.warn("Mobilized Plone site must be configured to be accessed using subdomains.")
        logger.warn("Otherwise preview and mobile site access.")
        logger.warn("Add following to your /etc/hosts:")
        logger.warn("127.0.0.1 mobi.site.foo web.site.foo preview.site.foo")
        logger.warn("..and access site site using fake domain name web.site.foo.")
        logger.warn("Also DO NOT do Zope HTTP Basic Auth, since it is not subdomain aware - use only Plone interface for login")        
        logger.warn("See twinapex.plone.mobile.monkeypatch for more info")
    
    if len(domain.split(".")) == 1:
        raise RuntimeError("You need to use subdomain to access the site. E.g. web.localhost instead of localhost")
    
    domain_root = ".".join(domain.split(".")[1:])
    
    return "." + domain_rot


def updateCredentials(self, request, response, login, new_password):
    """ Respond to change of credentials (NOOP for basic auth). """
    
    
    cookie_str = '%s:%s' % (login.encode('hex'), new_password.encode('hex'))
    cookie_val = encodestring(cookie_str)
    cookie_val = cookie_val.rstrip()
    
    domain = getCookieDomain(request)
    
    response.setCookie(self.cookie_name, quote(cookie_val), path='/', domain=domain)

def resetCredentials(self, request, response):
    """ Raise unauthorized to tell browser to clear credentials. """
    domain = getCookieDomain(request)
    response.expireCookie(self.cookie_name, path='/', domain=domain)

CookieAuthHelper.resetCredentials = resetCredentials

