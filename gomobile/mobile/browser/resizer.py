"""

    Simple image resizer view.

    Resize arbitary Zope images for mobile consumption.


    @deprecated: Please use imageprocessor module and @@mobile_image_processor view instead.

"""


__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"

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


def getUserAgentBasedResizedImageURL(context, request, *args, **kwargs):
    """ Get device-sensitive image URL.

    Add device user agent hash to image URL so that caches won't mix different user agent images.
    """

    context = aq_inner(context)
    # Will raise ComponentLookUpError
    name = "mobile_image_resizer"
    view = getMultiAdapter((context, request), name=name)

    view = view.__of__(context)

    # Make user that each user agent gets its own logo version and not cached version for some other user agent
    user_agent_md5 = get_user_agent_hash(request)

    kwargs["user_agent_md5"] = user_agent_md5

    return getResizedImageURL(*args, **kwargs)


def getRecommendedDimensions(device_size, recommend_size, fallback_size=(128,128), padding=(0,0), safe=(1000,1000)):
    """ Calculate image dimensions so that it will suitable for the mobile screen

    @param device_size: (device screen width, device screen height) or None if not known

    @param recommend_size: (width, height)

    @param fallback_size: (width, height)

    @param padding: (reduced width, reduced height)

    @param safe: (max width, max height)

    If device screen size is not known it can be None.

    For recommend size width/height can be string "auto" or integer value.

    Fallback size is used if recommend width/height is set to auto and device size is not known.

    Padding is removed from the dimensions after calculating the correct image size (to leave space for CSS margins)

    If safety parameters are exceeded, Unauthorized exception will be risen.

    @return: (width, height) for recommended aspect ration conserving resize
    """

    max_width = recommend_size[0]

    max_height = recommend_size[1]

    # Solve wanted width
    if max_width == "auto":

        if device_size:
            width = device_size[0]

            # TODO: Hardcoded hack
            if width > 320:
                width = 320
        else:
            width = 0

        if width <= 1:
            #print "Using default canvas width"
            width = fallback_size[0]

    else:
        width = int(recommend_size[0])

    width -= padding[0]

    # Solve wanted height
    if max_height == "auto":

        # twinapex.sniffer middleware inserts this

        if device_size:
            height = device_size[1]
        else:
            height = 0

        if height <= 1:
            print "Using default canvas height"
            height = fallback_size[1]

    else:
        height = int(recommend_size[0])

    if width < 1 or width > safe[0]:
        raise Unauthorized("Invalid width: %d" % width)

    if height < 1 or height > safe[1]:
        raise Unauthorized("Invalid height: %d" % height)

    return (width, height)

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


        # print "Resizer got browser:" + str(browser)


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
                # print "Using default canvas width"
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

        # print "Resizing %d %d" % (width, height)

        data, format = tool.getResizedImage(params["path"], width, height, conserve_aspect_ration=conserve_aspect_ration)

        self.request.response.setHeader("Content-type", "image/" + format)

        if isinstance(data, StringIO):
            # Looks like ZMedusa server cannot stream data to the client...
            return data.getvalue()

        return data





