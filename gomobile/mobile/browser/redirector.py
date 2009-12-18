"""

    Redirect requests arriving to web site to the mobile site.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__author_url__ = "http://www.twinapex.com"

from Products.Five.browser import BrowserView

from zope.app.component.hooks import getSite
from zope.component import getUtility, queryMultiAdapter

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType, IUserAgentSniffer, IMobileSiteLocationManager

class Redirector(BrowserView):
    """

    Manage redirect state in a cookie.

    If a request arrives with GET parameter force_web then set a cookie which
    makes web session persistent.

    Otherwise redirect the user to the mobile site if mobile user agent is sniffed.
    """

    # If cookie is set and contains value "web" then stay on the web site
    # even though
    COOKIE_NAME = "mobile_mode"


    def isSniffedMobile(self):
        """
        """

        site = getSite()

        # Force mobile mode if incoming device is mobile
        ua = queryMultiAdapter((site, self.request), IUserAgentSniffer)
        if ua:
            # This attribute is supported by pywurlf only
            if ua.get("is_wireless_device") == True:
                return True

        return False


    def isCookiedWeb(self):
        """
        """
        return self.request.cookies.get(Redirector.COOKIE_NAME) == "web"

    def isMobileWantsWeb(self):
        """
        Mobile site link which ought to force web mode.

        Check "force_web" GET parameter.

        @return True: If stay in web
        """
        return "force_web" in self.request.form

    def forceWeb(self):
        response = self.request.response
        response.setCookie(Redirector.COOKIE_NAME, "web", path="/")

    def redirect(self):
        """ Redirects to the mobile site, but stays on the same page.
        """
        url = self.request.URL
        location_manager = getUtility(IMobileSiteLocationManager)
        new_url = location_manager.rewriteURL(self.request, MobileRequestType.MOBILE)
        self.request.response.redirect(new_url)

    def intercept(self):
        """ Manage mobile redirect on-demand basis.

        @return: True if redirect has been made
        """
        if self.isSniffedMobile():

            # Check taht if we are asked to stay on the web site
            if self.isMobileWantsWeb():
                self.forceWeb()
                return False
            elif self.isCookiedWeb():
                return False

            return self.redirect()

        else:
            # A web browser
            return False
