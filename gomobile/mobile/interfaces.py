__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager


class IMobileContentish(zope.interface.Interface):
    """ Marker interface applied to all content objects which can potentially obey mobile behaviors """

class IMobileLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.

    This layer is applied on HTTPRequest when mobile rendering
    is on. Mobile only viewlets can be registered on this layer.
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
    """ Determine what content medias and use-cases the request presents.

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


class IMobileTracker(zope.interface.Interface):
    """ Mobile site analytics tracking provider.

    Mobile tracker provides necessary HTML
    snippet for site visitor tracking.

    Tracking providers are as Zope component adapters for context, request and name.
    They are similar to views in this sense.

    Example registration::

        @grok.adapter(zope.interface.Interface, zope.publisher.interfaces.browser.IBrowserRequest, name="bango")
        @grok.implementer(IMobileTracker)
        class BangoTracker(object):
            ...

    The site manager can change the active tracker backend in mobile_properties.
    Tracking viewlet does the corresponding tracker look-up based on this name.
    """

    def track(self, trackingId):
        """ Create tracking HTML snippet.

        @param trackingId: Tracker id. Site manager can edit this in the site settings.
            Tracker id is given by the tracker site and is unique to it. Any string values accepted.

        @return: HTML snippet as a string
        """

