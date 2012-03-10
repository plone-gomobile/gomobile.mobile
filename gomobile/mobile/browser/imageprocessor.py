"""

    Caching mobile image resizer.

    Resizer both Zope internal and arbitary URL image resources.

"""


__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext"

import os
import md5
import urllib
import logging
import shutil
from cStringIO import StringIO

from AccessControl import Unauthorized
from Acquisition import aq_inner
import zope.interface

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility, queryUtility
from zope.app.container.interfaces import INameChooser
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.browser import ploneview
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite
from plone.app.redirector.storage import RedirectionStorage

from mobile.sniffer.utilities import get_user_agent, get_user_agent_hash

from mobile.htmlprocessing.transformers.imageresizer import ImageResizer

from gomobile.mobile.interfaces import IMobileImageProcessor, IUserAgentSniffer
from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType
from gomobile.imageinfo.interfaces import IImageInfoUtility
from gomobile.mobile.utilities import getMobileProperties

# To not exceed this resize dimensions
safe_width = 1000
safe_height = 1000

logger = logging.getLogger("Resizer")

# Debug variable for unit tests
cache_hits = 0

DEFAULT_CACHE_PATH="/tmp/gomobile_image_cache"

VIEW_NAME = "@@mobile_image_processor"

class FSCache(object):
    """ Simple balanced folder based file system cache for images.

    Use cron job + timestamps to invalidate the cache.

    Each file path and name is hex digest of MD5 calculated from the cache key.
    Files are created in folder structure nested two levels to avoid too many files per one folder::

        DEFAULT_CACHE_PATH/00/00/000012341234
        DEFAULT_CACHE_PATH/00/10/001012341234
        DEFAULT_CACHE_PATH/10/00/100012341234
        DEFAULT_CACHE_PATH/10/10/101012341234

    """
    def __init__(self, root_path):
        self.root_path = root_path

    def makePathKey(self, ob):
        """
        Calculate hex digest.
        """
        ikey = str(ob)
        return md5.new(ikey).hexdigest()

    def get(self, key, default=None):
        """ Get the cached file and update its timestamp.

        @return: Path to cached file or None if not cached
        """

        global cache_hits

        logger.debug("Checking resizer image cache for " + key)

        work_dir, path = self.getOrCreatePath(key)
        if not os.path.exists(path):
            return default
        else:

            # http://stackoverflow.com/questions/1158076/implement-touch-using-python
            # We set both access time and modified time, as the file may be
            # on relatime file system
            os.utime(path, None)
            cache_hits += 1
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
        logger.debug("Created image cache file:" + full)
        #os.rename(temp, full)
        # Fix for freebsd http://code.google.com/p/plonegomobile/issues/detail?id=9
        shutil.move(temp, full)

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

    def invalidate(self):
        """ Nuke all files from the cache.

        One should do something smarter here.
        """
        if os.path.exists(self.root_path):
            shutil.rmtree(self.root_path)

class HTMLMutator(ImageResizer):
    """
    Rewrite <img> in HTML content code.

    Use mobile.htmlprocessing package and provide Plone specific callbacks.
    """

    def __init__(self, baseURL, trusted, rewriteCallback):
        ImageResizer.__init__(self, baseURL, trusted)
        self.rewriteCallback = rewriteCallback

    def rewrite(self, url):
        return self.rewriteCallback(url)

class MobileImageProcessor(object):

    zope.interface.implements(IMobileImageProcessor)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def init(self):
        self.site = getSite()
        self.cache = FSCache(self.getCachePath())

    def getSecret(self):
        """ Avoid properties look up using cached value.

        @return: Unguessable string, unique to a site
        """
        _secret = self.site.portal_properties.mobile_properties.image_resizer_secret
        return _secret


    def calculateSignature(self, **kwargs):
        """ Calculate protected MD5 for resizing parameters, so that input is protected against DoS attack """

        logger.debug("Calculating signature from params:" + str(kwargs))

        # Sort parameters by key name, as MD5 function
        # is sensitive to the order of the parameters
        # and Python dict does not guarantee the order
        params = list(kwargs.items())

        def key_comparison(x, y):
            """
            """
            return cmp(x[0], y[0])

        params.sort(key_comparison)

        concat = ""
        for key, value in params:
            concat += key + "=" + str(value)
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

    def removeScale(self, imagePath):
        """
        Helper function to remove scale view name from the image path.

        @param imagePath: Site root relative path to the image as list.
        """
        last = imagePath[-1]

        # Assume ATContentType image scales
        if last.startswith("image_"):
            imagePath = imagePath[0:-1]

        return imagePath

    def mapURL(self, url):
        """ Make image URL relative to site root.

        If possible, make URI relative to site root
        so that we can safely pass it around from a page to another.

        If URL is absolute, don't touch it.

        @param url: Image URL or URI as a string
        """

        rs = RedirectionStorage()
        if rs.has_path(url):
            url = rs.get(url)


        # Make sure we are traversing the context chain without view object messing up things
        context = self.context.aq_inner

        if url.startswith("http://") or url.startswith("https://"):
            # external URL
            url = url
        elif "++resource" in url:
            # Zope 3 resources are mapped to the site root
            url = url
        else:
            # Map the context path to the site root
            if url.startswith("/"):
                # Pass URL to resizer view relocated to the site root

                url = url[1:]
            else:
                # The URL is relative to the context path
                # Map URL to be relative to the site root

                site = getSite()

                try:
                    imageObject = context.unrestrictedTraverse(url)
                except Unauthorized:
                    # The parent folder might be private and the image public,
                    # in which case we should be able to view the image after all.
                    parent_path = '/'.join(url.split('/')[:-1])
                    image_path = url.split('/')[-1]
                    parent = site.unrestrictedTraverse(parent_path)
                    imageObject = parent.restrictedTraverse(image_path)

                if ("FileResource" in imageObject.__class__.__name__):
                    # Five mangling compatible way to detect image urls pointing to the resource directory
                    # ...but this should not happen if images are accessed using ++resource syntax
                    return url
                elif hasattr(imageObject, "getPhysicalPath"):
                    physicalPath = imageObject.getPhysicalPath() # This path is relative to Zope Application server root
#
                    virtualPath = self.request.physicalPathToVirtualPath(physicalPath)

                    # TODO: Assume Plone site is Zope app top level root object here

                    # empty root node, site node
                    assert len(physicalPath) > 2

                    virtualPath = physicalPath[2:]

                    virtualPath = self.removeScale(virtualPath)

                    url = "/".join(virtualPath)
                else:
                    raise RuntimeError("Unknown traversable image object:" + str(imageObject))
        return url

    def getImageDownloadURL(self, url, properties={}):
        """
        Return download URL for image which is put through image resizer.

        @param url: Source image URI, relative to context, or absolite URL

        @param properties: Extra options needed to be given to the resizer, e.g. padding, max width, etc.

        @return: String, URL where to resized image can be downloaded. This URL varies
            by the user agent.
        """
        self.init()

        url = self.mapURL(url)

        # Prepare arguments for the image resizer view
        new_props = {"conserve_aspect_ration" : "true"}
        new_props.update(properties)
        new_props["url"] = url

        if self.isUserAgentSpecific(url, new_props):
            # Check if the result may vary by user agnt
            new_props["user_agent_md5"] = get_user_agent_hash(self.request)

        new_props = self.finalizeViewArguments(new_props)

        return self.site.absolute_url() + "/" + VIEW_NAME + "?" + urllib.urlencode(new_props)


    def processHTML(self, data, trusted):
        """ Process all <img> tags in HTML code.

        Some error filtering is performed for incoming string data,
        as there are some common cases related to browser based WYSIWYG
        which will make shit hit the fan.

        @param base_url: Base URL of HTML document - for resolving relative img paths

        @return: Mutated HTML output as a string
        """

        self.init()

        base = self.context.absolute_url()

        # create mobile.heurestics helper
        mutator = HTMLMutator(base, trusted, self.getImageDownloadURL)

        if type(data) == str:
            data = unicode(data, "utf-8", errors="ignore")

        # Need to fix Windows style new lines here or they will cause extra new lines in the output
        data = data.replace(u"\r", u"")

        # Need to fix Unicode non-breaking space bar (&nbsp;) or it will be escaped in the output and appears wrong
        # Use XML/XHTML entity &#160; to present this evil character
        data = data.replace(u"\xA0", u"&#160;")

        processed = mutator.process(data)

        return processed

    def getCachePath(self):
        """
        @return: FS path where cached resized scales are stored
        """
        image_resize_cache_path = getattr(self.context.portal_properties.mobile_properties, "image_resize_cache_path", DEFAULT_CACHE_PATH)
        return image_resize_cache_path



class ResizeViewHelper(BrowserView):
    """
    Base class from where you can derivate your own image resizers or call this as a helper from your own views.

    """

    def init(self):

        self.resizer = getMultiAdapter((self.context, self.request), IMobileImageProcessor)
        self.resizer.init()

        sniffer = getMultiAdapter((self.context, self.request), IUserAgentSniffer)
        self.ua = sniffer.getUserAgentRecord()


    def buildCacheKey(self, width, height):
        """
        Build cache key for result image data.

        This varies by width and height if we know them.
        If we don't know, then we user agent string itself as a part of the key,
        so that different mobiles don't get wrong image from the cache.
        """

        # We know the user agent so we know the resulting width and height in this stage
        if self.ua:
            key = str(width) + "-" + str(height) + "-"
        else:
            key = get_user_agent_hash(self.request)

        def add_param(key, value):
            key += "-"
            key += str(value)
            return key

        key = add_param(key, self.cache_key)
        key = add_param(key, self.conserve_aspect_ration)
        key = add_param(key, self.padding_width)

        return key

    def parseParameters(self, parameters):
        """ Parse parameters needed for

        """
        self.width = parameters.get("width", "auto")
        self.height = parameters.get("height", "auto")
        self.padding_width = parameters.get("padding_width", 0)
        self.conserve_aspect_ration = parameters.get("conserve_aspect_ration", False)

        self.image = parameters.get("image", None)
        self.url = parameters.get("url", None)

        if not(self.image or self.url):
            raise RuntimeError("Needs either image or URL parameter")

        self.cache_key = parameters.get("cache_key", self.url)
        if not self.cache_key:
            raise RuntimeError("cache_key or URL parameter must be provided")

    def resolveCacheFormat(self, data):
        """
        Peek cached file first bytes to get the format.
        """
        if data[0:3] == "PNG":
            return "png"
        elif data[0:3] == "GIF":
            return "gif"
        else:
            return "jpeg"


    def serve(self, width, height):
        """ Generate resized image or fetch one from cache.

        TODO: Clear up string / StringIO madness here in all those ifs
        """
        key = self.buildCacheKey(width, height)
        path = self.resizer.cache.makePathKey(key)
        logger.debug("Performing mobile image resize cache look up " + key + " mapped to " + path)

        file = self.resizer.cache.get(path)
        if file:
            f = open(file, "rb")
            data = f.read()
            f.close()
            format = self.resolveCacheFormat(data)
            value = data
        else:
            tool = getUtility(IImageInfoUtility)

            logger.debug("Resizing image to mobile dimensions %d %d" % (width, height))

            if self.url:
                data, format = tool.getURLResizedImage(self.url, width, height, conserve_aspect_ration=self.conserve_aspect_ration)
            else:
                data, format = tool.resizeImage(self.image, width, height, conserve_aspect_ration=self.conserve_aspect_ration)

            # Mercifully cache broken images from remote HTTP downloads
            if data is None:
                value = ""
            else:
                value = data.getvalue()

            self.resizer.cache.set(path, value)

        if value == "":
            # We could not access the orignal image data
            self.request.response.setHeader("Content-type", "text/plain")
            return "Image resize error"

        self.request.response.setHeader("Content-type", "image/" + format)

        # TODO: Check whether we can stream response (no memory buffering)

        if hasattr(data, "getvalue"):
        # Looks like ZMedusa server cannot stream data to the client...
        # so we need to return it as memory buffered
            return data.getvalue()

        return data

    def resolveDimensions(self):
        """ Calculate final dimensions for the image.
        """

        if self.ua:
            logger.debug("Using user agent:" + str(self.ua.getMatchedUserAgent()))
        else:
            logger.debug("No user agent available for resolving the target image size")

        if self.ua:
            canvas_width = self.ua.get("usableDisplayWidth")
            canvas_height = self.ua.get("usableDisplayHeight")
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
            width = self.width

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

        return width, height

    def __call__(self, parameters):

        self.init()
        self.parseParameters(parameters)
        width, height = self.resolveDimensions()
        return self.serve(width, height)


class ResizeView(ResizeViewHelper):
    """ Resizer view for arbitary images looked up by URL or Zope path.

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

    The image results are cached on file-system. The cache path is configurable
    through *image_resize_cache_path* mobile parameter and defaults to /tmp/gomobile_image_cache.
    The cache is never cleaned up, so you are responsible to set a scheduled
    task to remove old files.
    """


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
        self.cache_key = self.url

    def checkSecret(self):
        """ Harden us against DoS attack.

        All query parameters are signed and check if the caller knows the correct signature.
        """

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
            secret = params.get("secret", None)
            if secret:
                del params["secret"]

            calculated = self.resizer.calculateSignature(**params)

            if calculated != secret:
                raise Unauthorized("Bad image resizer secret:" + str(secret) + " calculated:" + str(calculated))



    def __call__(self):
        """
        """

        self.init()

        self.parseParameters()

        self.checkSecret()

        width, height = self.resolveDimensions()

        return self.serve(width, height)

class ClearCacheView(BrowserView):
    """
    Expose clearing of mobile cache as s view.
    """

    def __call__(self):
        """
        TODO: Implement some smart timestamp checking here.
        """

        resizer = getMultiAdapter((self.context, self.request), IMobileImageProcessor)

        resizer.init()

        # Check that the caller knows the secret
        secret = self.request.form.get("secret", None)
        if secret != resizer.getSecret():
            raise Unauthorized("Wrong secret:" + secret)

        resizer.cache.invalidate()

        properties = getMobileProperties(self.context.aq_inner, self.request)
        cache_folder = properties.image_resize_cache_path

        return "Cache has been cleared:" + cache_folder

class IHTMLImageRewriter(zope.interface.Interface):
    """
    Declare RestrictedPython safe functions for HTMLImageRewriter view.
    """

    def processHTML(html, trusted):
        pass

class HTMLImageRewriter(BrowserView):
    """
    Template helper view to rewrite HTML structure <img> tags.

    For example, see document_view.pt in gomobiletheme.basic.

    Related tests are in gomobiletheme.basic.tests.
    """

    def processHTML(self, html, trusted=True, only_for_mobile=False):
        """ Rewrite HTML for mobile compatible way.

        @param html: HTML code as a string

        @param trusted: If True do not clean up nasty tags like <script>

        @param only_for_mobile: Perform processing only if the site is rendered in mobile mode
        """


        if only_for_mobile:
            # Perform check if we are in mobile rendering mode
            discriminator = getUtility(IMobileRequestDiscriminator)
            flags = discriminator.discriminate(self.context, self.request)
            if not MobileRequestType.MOBILE in flags:
                return html

        resizer = getMultiAdapter((self.context, self.request), IMobileImageProcessor)
        resizer.init()
        if html is not None and html != "":
            # lxml bails out if input is not sane
            return resizer.processHTML(html, trusted)
        else:
            return html

    def __call__(self):
        """
        """
        raise RuntimeError("Please do not call this view directly - instead use processHTML() method")

