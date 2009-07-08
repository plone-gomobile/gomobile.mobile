__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager

class IMobileLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    
    This layer is applied on HTTPRequest when mobile rendering 
    is on.    
    """
    
class IMobileUtility(zope.interface.Interface):
    """ Helper function to deal with mobile requests. """
    
class MobileRequestType:
    """ Pseudoconstant flags how HTTP request can relate to mobility """
    
    # Admin web page
    ADMIN = "admin"
    
    # Anonymous web page
    WEB = "web"
    
    # Mobile page
    MOBILE = "mobile"
    
    # Preview mobile page
    PREVIEW = "preview"
    
    

class IMobileRequestDiscriminator(zope.interface.Interface):
    """ Determine if the request is a mobile or not. 
        
    """

    def isMobileRequest(context, request):
        """ Is the HTTP request a mobile version.
        
        If the request is mobile request
        
            - Mobile skin layer will be applied
            
            - Navigation will be mobile based
            
        @param context: PloneSite object
        
        @param request: HTTPRequest
        
        @return: True if the request output is targeted to mobile site.
        """
        
    def isPreviewRequest(context, request):        
        """
        
        Preview requests are mobile pages rendered in IFRAME.
        They need special handling, because they load simulator
        specific Javascript files.

        @param context: PloneSite object

        @param request: HTTPRequest
        
        @return: True if the request output is targeted to preview IFRAME        

        """
        
    def isAdminRequest(context, request):    
        """ Is the request mobile site administration request.
        
        The admin request will render the site in normal web mode,
        but mobile only content is visibile in folder listings
        and navigation tree. For the simple fact, that 
        you need to access mobile content to be able to edit it.

        @param context: PloneSite object
        
        @param request: HTTPRequest
        
        @return: True if the request output should render mobile only specific content on 
                 normal web view
        """
        
    def discriminate(context, request):
        """ Flag request to describe its relation of mobile
        
        Wrapper which calls everyone of above methods.    
        
        This function just exist to make your life easier.
        
        The result is allowed to be cached internally.
        
        @return list of strings of MobileRequestType flags
        """
        
class IMobileSiteLocationManager(zope.interface.Interface):
    """ Use cookie based switching for web/mobile mode rendering.

    1. Set necessary cookies which tell whether the site should be rendered
      in web or mobile mode
    
    2. Redirect to different URL
    """
    
    
      
    
    def rewriteURL(request, url, mode):
        """ Rewrite the URL to redirect to the page in a different mobile view mode.
        
        @param mode: One of MobileRequestType pseudo constants
        
        @return: string
        """
        
      
