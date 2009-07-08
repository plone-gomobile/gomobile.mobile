__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import urlparse

import zope.interface

from Products.Five.browser import BrowserView

from zope.component import getUtility, queryUtility

from gomobile.mobile.interfaces import IMobileUtility

class MobileUtility(object):
    """ Zope 3 utility for mobile actions. """
    
    zope.interface.implements(IMobileUtility)
    
    def isMobileRequest(self, request):
        """ Determine should this request be rendered in mobile mode. """        
            
        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True
        
        if "HTTP_HOST" in request.environ:
            # Unit tests don't have this
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
    
       
class MobileTool(BrowserView):
    """ Traversable mobile utility. """
    
    def getUtility(self):        
        return getUtility(IMobileUtility)
    
    def replaceNetworkLocation(self, url, newNetLocation):
        parts = urlparse.urlparse(url)
        parts = list(parts)
        parts[1] = newNetLocation
        return urlparse.urlunparse(parts)
    
    def isMobileRequest(self):
        return self.getUtility().isMobileRequest(self.request)        
    
    def isPreviewRequest(self):
        return self.getUtility().isPreviewRequest(self.request)            
    
    def getMobileSiteURL(self):
        """ Return the mobile version of this of """
        base = self.context.portal_properties.mobile_properties.mobile_site_base
        return self.replaceNetworkLocation(self.context.absolute_url(), base)
    
    def getMobilePreviewURL(self):
        """ Return URL used in phone simualtor.
        
        We do here little ugly magic, because IFRAME forces
        us to use same domain for parent and child document, or
        cross frame JS does not work.
        """
        base = self.context.portal_properties.mobile_properties.preview_site_base
        return self.replaceNetworkLocation(self.context.absolute_url(), base)
        
    def getWebSiteURL(self):
        """ Return the mobile version of this of """
        base = self.context.portal_properties.mobile_properties.web_site_base
        return self.replaceNetworkLocation(self.context.absolute_url(), base)
    
