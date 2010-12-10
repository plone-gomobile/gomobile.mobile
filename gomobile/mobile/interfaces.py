__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import zope.interface
from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager


class IMobileContentish(zope.interface.Interface):
    """ Marker interface applied to all content objects which can potentially obey mobile behaviors """

class IGoMobileInstalled(IDefaultPloneLayer):
    """
    Mark that gomobile.mobile package is installed on the site.
    """

class IMobileLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.

    This layer is applied on HTTPRequest when mobile rendering
    is on. Mobile only viewlets can be registered on this layer.
    """

class IMobileUtility(zope.interface.Interface):
    """ Helper function to deal with mobile requests. """

class MobileRequestType:
    """ Pseudoconstant flags how HTTP request can relate to mobility """

    # Admin web page - show both mobile and web content items in admin UI
    ADMIN = "admin"

    # Anonymous web page - show web only items
    WEB = "web"

    # Mobile page - show mobile items
    MOBILE = "mobile"

    # Preview mobile page
    PREVIEW = "preview"


class IMobileRequestDiscriminator(zope.interface.Interface):
    """ Determine what content medias and use-cases the request presents.

    Example::

            from zope.component import getUtility
            from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType

            discriminator = getUtility(IMobileRequestDiscriminator)
            flags = discriminator.discriminate(self.context, self.request)
            if MobileRequestType.MOBILE in flags:
                # Do mobile
            else:
                # Do web


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

    def rewriteURL(url, mode):
        """ Rewrite the URL to redirect to the page in a different mobile view mode.

        @param mode: One of MobileRequestType pseudo constants

        @return: string
        """

class IMobileRedirector(zope.interface.Interface):
    """ Manage whether the user wants to surf web or mobile site.

    Disable automatic, user-agent based redirects, if needed
    by fiddling with cookies.

    View like multi-adapter with parameters:

    * context

    * request
    """

    def intercept():
        """ Create HTTP redirect response to the mobile site if needed.

        @return: True if redirect was made.
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

    def track(self, trackingId, debug):
        """ Create tracking HTML snippet.

        @param trackingId: Tracker id. Site manager can edit this in the site settings.
            Tracker id is given by the tracker site and is unique to it. Any string values accepted.

        @param debug: Set to true to additional logging output and debug HTTP response headers

        @return: HTML snippet as a string
        """

class IMobileImageProcessor(zope.interface.Interface):
    """ Helper for making images behave nicely with mobile.

    View like multi-adapter with parameters:

    * context

    * request

    This helper is able to rewrite

    * Individual image urls to be processed for mobile

    * HTML snippets

    Accepts both internal and external image source links.
    All internal links are assumed to be relative to context.absolute_url().

    Possible properties for resized images:

    * width: "auto" to set width to user agent max screen width or integer

    * height: "auto2 to set height to user agent max screen height or integer

    * padding_width: How many pixels of width padding is subtracted from the result
      width. Integer.

    * conserve_aspect_ration: true or false string. Default is false.


    """

    def getImageDownloadURL(url, properties):
        """ Rewrite <img src=""> URL so that image is processed through resizer.

        The original URL is returned if the processer thinks the resizer
        cannot handle this sort of image.

        The default operation is to scale down image conserving
        aspect ration so that both width and height fits to the mobile phone screen.
        Mobile phone screen is picked from user agent database. If database or
        database entry is not available, use width and height defaults configured
        for the site.

        @properties: Dictionary of directives how image should be processed e.g.
            is padding added.

        @return: URL as a string.
        """

    def processHTML(data, trusted, only_for_mobile):
        """ Process all <img> tags in HTML code.

        This may also perform cross-site scripting
        attack preventation.

        @param data: HTML code as unicode or UTF-8 string

        @param only_for_mobile: If set True, touch HTML only if the site is currently rendered in mobile mode.
            This is handy for converged sites.

        @param trusted: Is parsed HTML from trusted source (run XSS clean-up)

        @return: Mutated XHTML output as a string. Always UTF-8 encoded.
        """


class IUserAgentSniffer(zope.interface.Interface):
    """ Get user agent info for HTTP request.

    This is an adapter which returns mobile.sniffer.UserAgent records
    for the HTTP request.
    By overriding the adapter you can add site specific user agent sniffing logic.

    This is a multi-adapter with two parameters:

        * context object (site)

        * request (HTTP request object)

    See gomobile.mobile.sniffer for the default implementation.


    """

    def isMobileBrowser():
        """ Check whether the HTTP request was web or mobile browser request.

        Perform a brand recogniziation regular expressions against
        the user agent string.

        @return: True if HTTP request was made by a mobile browser
        """

    def getUserAgentRecord():
        """ Get the underlying mobile.sniffer.UserAgent record for the HTTP request.

        Example how to use::
            from zope.component import queryMultiAdapter
            # ua is mobile.sniffer.UserAgent object or None if no match/a web browser
            ua = queryMultiAdapter((context, request), IUserAgentSniffer)

        @return: mobile.sniffer.base.UserAgent instance of None
        """
