"""

    Utility facilities to deal with mobile HTTP requests.

"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import urlparse

import zope.interface
from zope.component import getUtility, queryUtility

from mobile.sniffer.utilities import get_user_agent, is_low_end_phone

from Products.Five.browser import BrowserView
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