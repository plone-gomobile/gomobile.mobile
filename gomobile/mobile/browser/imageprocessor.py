"""

    Caching mobile image resizer.

    Resizer both Zope internal and arbitary URL image resources.

"""


__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"

import os
import md5
import urllib
from StringIO import StringIO

from AccessControl import Unauthorized
from Acquisition import aq_inner
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

from mobile.sniffer.utilities import get_user_agent, get_user_agent_hash

from mobile.htmlprocessing.transformers.imageresizer import ImageResizer

from gomobile.mobile.interfaces import IMobileImageResizer, IUserAgentSniffer
from gomobile.imageinfo.interfaces import IImageInfoUtility

# To not exceed this resize dimensions
safe_width = 1000
safe_height = 1000

class FSCache(object):
    """ Simple balanced folder based file system cache for images.
    
    Use cron job + timestamps to invalidate the cache.
    """
    def __init__(self, root_path):
        self.root_path = root_path
        
    def makePathKey(self, ob):
        ikey = str(ob)
        return md5.new(ikey).hexdigest()

    def get(self, key, default=None):
        """
        @return: Path to cached file or None if not cached
        """
        path = self.getOrCreatePath(key)
        if not os.path.exists(key):
            return default
        else:
            return path
        
    def getOrCreatePath(self, key):
        """
        @return: tuple (work dir path, final file path)
        """
        path1 = key[0:2]
        path2 = key[2:4]
        
        # TODO: Do this only once and get rid of this 
        #fspermissions.ensure_writable_folder(storage_folder)
        #fspermissions.ensure_writable_folder(os.path.join(storage_folder, path1))
        #fspermissions.ensure_writable_folder(os.path.join(storage_folder, path1, path2))
        path = os.path.join(self.root_path, path1, path2)
        
        if not os.path.exists(path):
            os.makedirs(path, 0x1FF)
        
        full_path = os.path.join(path, key)

        return path, full_path
    
    def makeTempFile(self, work_path):
        """
        """
        return os.path.join(work_path, os.tmpnam())
    
        
    def closeTempFile(self, temp, full):
        """ Perform final cache set as atomic FS operation.
        """
        os.rename(temp, full)
        
    def set(self, key, value):
        """
        """
        work_path, file_path = self.getOrCreatePath(key)
        
        # Create a cached copy
        temp = self.makeTempFile(work_path)
        file = open(temp, "wb")
        file.write(value)
        file.close()
        
        self.closeTempFile(temp, file_path)
        
        
class HTMLMutator(ImageResizer):
    """
    Rewrite <img> in HTML content code…
    """
    
    def __init__(self, baseURL, trusted, rewriteCallback):
        ImageResizer.__init__(baseURL, trusted)
        self.rewriteCallback = rewriteCallback
        
    def rewrite(self, url):
        return self.rewriteCallback(url)
        
class MobileImageResizer(object):
    
    zope.interface.implements(IMobileImageResizer)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.site = getSite()
        

    def getSecret(self):
        """ Avoid properties look up using cached value.
        
        @return: Unguessable string, unique to a site
        """
        _secret = self.site.portal_properties.mobile_properties.image_resizer_secret
        return _secret
    
    
    def calculateSignature(self, **kwargs):
        """ Calculate protected MD5 for resizing parameters, so that input is protected against DoS attack """
    
        for key, value in kwargs.items():
            concat = key + "=" + str(value)
        concat += self.getSecret()
        return md5.new(concat).hexdigest()

    def isUserAgentSpecific(self, url, properies):
        """ Determine whether the result of resize may vary by user agent. 
         
        If we need to vary by user agent, insert a string based 
        on HTTP_USER_AGENT to the resizer GET query.
        """
        return True
        
    def finalizeViewArguments(self, properties):
        """
        Make sure that input parameters are URL compliant.
        """
        for key, val in properties.items():
            properties[key] = str(val)

        # Make it so that no one else can guess working resizer URLs
        secret = self.calculateSignature(**properties)
        properties["secret"] = secret
        return properties
    
    def mapURL(self, url):
        """
        Make image URL relative to site root.
        """
        if url.startswith("http://"):
            # external URL
            url = url
        else:
            # Map the context path to the site root
            if url.startswith("/"):
                # Pass URL to resizer view relocated to the site root
                url = url[1:]
            else:
                # The URL is relative to the context path
                # Map context to the site root
                imageObject = self.context.unrestrictedTraverse(url)
                physicalPath = imageObject.getPhysicalPath() # This path is relative to Zope Application server root
                virtualPath = self.request.physicalPathToVirtualPath(physicalPath)
                url = virtualPath
                
        return url
        
    def getImageDownloadURL(self, url, properties={}):
        
        url = self.mapURL(url)
        
        # Prepare arguments for the image resizer view
        new_props = {}
        new_props.update(properties)        
        new_props[url] = url
        
        if self.isUserAgentSpecific(url, new_props):
            # Check if the result may vary by user agnt
            new_props["user_agent_md5"] = get_user_agent_hash(self.request)
        
        new_props = self.finalizeViewArguments(new_props)
        
        return self.site.absolute_url() + "/@@mobile_image_resizer?" + urllib.urlencode(new_props)
                
                
    def processHTML(self, data, trusted):
        """ Process all <img> tags in HTML code.

        @param base_url: Base URL of HTML document - for resolving relative img paths
        
        @return: Mutated HTML output as a string
        """
        base = self.context.absolute_url()
        mutator = HTMLMutator(base, trusted, self.getImageDownloadURL)
        processed = mutator.process(data)
        return processed
        
        
            
class ResizeView(BrowserView):
    """ Resize images on fly for mobile screens.

    Automatic width or height parameter can be used. In this case
    we see whether we have sniffed the mobile screen size based
    on user agent sniffer middle. Use mobile browser canvas
    dimension in this case.

    If width/height is automatic, but no browser information is available
    fallback to default setting set in mobile_properties.

    HTTP GET query parameters are generated by MobileImageResizer.getImageDownloadURL()

    Special parameters:
    
        * override_secret: Set this query parameteter to site resizer secret code setting
          to override DoS preventing parameter signature check.  
          Useful for debugging.
          
    """
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.resizer = getMultiAdapter((context, request), IMobileImageResizer)
    
    
    def parseParameters(self):
        """ Parse incoming HTTP GET parameters.
        
        """
        
        params = self.request.form
        
        padding_width = params.get("padding_width", "0")
        self.padding_width = int(padding_width)
        
        conserve_aspect_ration = params.get("conserve_aspect_ration", "false")
        self.conserve_aspect_ration = conserve_aspect_ration.lower() == "true"
        
        self.override_secret = params.get("override_secret", None)
        
        self.width = params.get("width", "auto")
        if self.width != "auto":
            self.width = int(self.width)
            
        self.height = params.get("height", "auto")
        if self.height != "auto":
            self.height = int(self.height)
            
        self.url = params.get("url", None) 
        
        
    def __call__(self):
        """
        """
        
        # Parse incoming 

        if self.override_secret:
            # Override parameter signature check
            # by directly providing shared secret as an HTTP query parameter
            # for testing.
            if self.override_secret != self.resizer.getSecret():
                raise Unauthorized("Wrong override_secret:" + self.override_secret)
        else:
            
            # Verify that secret signs all other parameters
            params = {} 
            params.update(self.request.form)
            secret = params["secret"]
            del params["secret"]
            
            if self.resizer.calculateSignature(**params) != secret:
                raise Unauthorized("Bad image resizer secret:" + str(secret) + " " + str(params))


        sniffer = getMultiAdapter((self.context, self.request), IUserAgentSniffer)
        ua = sniffer.getUserAgentRecord()
        
        if ua:
            canvas_width = ua.get("usableDisplayWidth")
            canvas_height = ua.get("usableDisplayHeight")
        else:
            canvas_width = None
            canvas_height = None
           
        # Fill in default info if user agent records are incomplete  
        if not canvas_width:
            canvas_width = self.context.portal_properties.mobile_properties.default_canvas_width
        
        if not canvas_height:
            canvas_height = self.context.portal_properties.mobile_properties.default_canvas_height
            

        # Solve wanted width
        if self.width == "auto":
            width = canvas_width
        else:
            width = self.widtht

        # Make sure we have some margin available if defined
        width -= self.padding_width

        # Solve wanted height
        if self.height == "auto":
            height = canvas_height
        else:
            # Defined as a param
            height = self.height

        if width < 1 or width > safe_width:
            raise Unauthorized("Invalid width: %d" % width)

        if height < 1 or height > safe_height:
            raise Unauthorized("Invalid height: %d" % height)

        tool = getUtility(IImageInfoUtility)

        print "Resizing %d %d" % (width, height)

        data, format = tool.getResizedImage(self.url, width, height, conserve_aspect_ration=self.conserve_aspect_ration)

        self.request.response.setHeader("Content-type", "image/" + format)

        if isinstance(data, StringIO):
            # Looks like ZMedusa server cannot stream data to the client...
            # so we need to return it as memory buffered
            return data.getvalue()

        return data






    


        