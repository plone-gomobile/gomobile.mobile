__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import md5
import urllib
from StringIO import StringIO

from AccessControl import Unauthorized
from zope.app.component.hooks import getSite
import zope.interface

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.browser import ploneview
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, queryUtility
from zope.app.component.hooks import getSite


from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, IMobileSiteLocationManager, MobileRequestType
from gomobile.imageinfo.interfaces import IImageInfoUtility
# Resizer     
_secret = None

# To not exceed this resize dimensions
safe_width = 1000
safe_height = 1000

def getSecret():
    """ Avoid properties look up using cached value """
    global _secret
    
    if not _secret:
        site = getSite()
        _secret = site.portal_properties.mobile_properties.image_resizer_secret
        
    return _secret
        
              
def calculateSignature(**kwargs):
    """ Calculate protected MD5 for resizing parameters, so that input is protected against DoS attack """

    for key, value in kwargs.items():
        concat = key + "=" + str(value)
    concat += getSecret()
    return md5.new(concat).hexdigest()


def getResizedImageQuery(**params):
    """ Convert parameters to HTTP GET query form and calculate protection signature for them """
    
    for key, val in params.items():
        params[key] = str(val)
    
    secret = calculateSignature(**params)
    
    params["secret"] = secret
    
    return params

def getResizedImageURL(*args, **kwargs):
    """ Get image URI which is resized version for the mobile screen.

    @param path: Zope traversing path to the image
    
    @param width: Target width or None for to use the mobile screen width
    
    @param width: Target height or None for to use the mobile screen height
    """
    
    if(len(args) > 0):
        raise RuntimeError("No nameless arguments allowed:" + str(args))
    
    site = getSite()
    query = getResizedImageQuery(**kwargs)
    return site.absolute_url() + "/@@mobile_image_resizer?" + urllib.urlencode(query)

class ImageResizerView(BrowserView):
    """ Resize images on fly for mobile screens.
    
    Respond to the request with image/png content.
    
    GET query parameters tell the wanted image dimensions. Query parameters
    are protected with md5 generated from a shared secret to prevent DoS 
    attacks. The image is identified by parameter 'path' which
    is Zope traversing path to the image.
    
    Automatic width or height parameter can be used. In this case
    we see whether we have sniffed the mobile screen size based
    on user agent sniffer middle. Use mobile browser canvas
    dimension in this case.
    
    If width/height is automatic, but no browser information is availabl,e
    fallback to default setting set in mobile_properties.    
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getResizedImageURL(self, *args, **kwargs):
        return getResizedImageURL(*args, **kwargs)

    def __call__(self):
        """ 
        """        
        params = {}
        params["path"] = self.request["path"]
        params["width"] = self.request["width"]
        params["height"] = self.request["height"]


        # Override parameter signature check
        # by knowing the shared secret
        override_secret = self.request.get("override_secret", None)

        if "padding_width" in self.request:
            padding_width = int(self.request["padding_width"])
        else:
            padding_width = 0

        params["conserve_aspect_ration"] = self.request.get("conserve_aspect_ration", None)

        
        secret = self.request["secret"]
        
        if override_secret:
            # Override parameter signature check
            # by directly providing shared secret as an HTTP query parameter
            # for testing.
            if override_secret != getSecret():
                raise Unauthorized("Wrong override_secret:" + override_secret)        
        else:
            if calculateSignature(**params) != secret:
                raise Unauthorized("Bad image resizer secret:" + str(secret) + " " + str(params))        
            

        if "browser" in self.request.environ:
            browser = self.request.environ["browser"]
            
            # TODO: Make something smarter here
            if browser.is_generic() or "Firefox" in browser.user_agent:
                # "Firefox" in browser.user_agent <-- what the shit is in the database??? firefox.canvas_width = 350
                browser = None
            
        else:
            browser = None
            
            
        print "Resizer got browser:" + str(browser)
        
       
        # Solve wanted width
        if params["width"] == "auto":
            
            # twinapex.sniffer middleware inserts this
                
            if browser:
                width = browser.canvas_width    
                
                # TODO: Hardcoded hack
                if width > 320:
                    width = 320                                            
            else:
                width = 0
                
            if width <= 1:
                print "Using default canvas width"
                width = self.context.portal_properties.mobile_properties.default_canvas_width
                
        else:
            width = int(params["width"])
            
        width -= padding_width

        # Solve wanted height
        if params["height"] == "auto":
            
            # twinapex.sniffer middleware inserts this
                
            if browser:
                height = browser.canvas_height
            else:
                height = 0
                
            if height <= 1:
                print "Using default canvas height"
                height = self.context.portal_properties.mobile_properties.default_canvas_height
                
        else:
            height = int(params["height"])
       
        if width < 1 or width > safe_width:
            raise Unauthorized("Invalid width: %d" % width)
        
        if height < 1 or height > safe_height:
            raise Unauthorized("Invalid height: %d" % height)        
        
        tool = getUtility(IImageInfoUtility)
                
        # Convert from string to Python bool
        if params["conserve_aspect_ration"]:
            conserve_aspect_ration = (params["conserve_aspect_ration"] != "False")
        else:
            conserve_aspect_ration = True
            
        print "Resizing %d %d" % (width, height)
                
        data, format = tool.getResizedImage(params["path"], width, height, conserve_aspect_ration=conserve_aspect_ration)
        
        self.request.response.setHeader("Content-type", "image/" + format)
        
        if isinstance(data, StringIO):
            # Looks like ZMedusa server cannot stream data to the client...
            return data.getvalue()
        
        return data
        
        
        
                                         
        
