"""

    Redirect requests arriving to web site to the mobile site.

    http://webandmobile.mfabrik.com

"""

__license__ = "GPL 2"
__copyright__ = "2009-2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>"

import logging

from Acquisition import aq_inner

from datetime import datetime

from zope.app.component.hooks import getSite
from zope.component import getUtility, queryMultiAdapter, getMultiAdapter
from OFS.interfaces import IApplication

from gomobile.mobile.interfaces import (
    IMobileRequestDiscriminator, MobileRequestType, IUserAgentSniffer,
    IMobileSiteLocationManager)

from mobile.sniffer.utilities import get_user_agent

logger = logging.getLogger('gomobile.mobile')


class Redirector(object):
    """

    Manage redirect state in a cookie.

    If a request arrives with GET parameter force_web then set a cookie which
    makes web session persistent.

    Otherwise redirect the user to the mobile site if mobile user
    agent is sniffed.
    """

    # If cookie is set and contains value "web" then stay on the web site
    # even though
    COOKIE_NAME = "mobile_mode"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def isSniffedMobile(self):
        """ Check if the current browser is mobile browser by nature.
        """

        site = getSite()

        # Force mobile mode if incoming device is mobile
        us = queryMultiAdapter((site, self.request), IUserAgentSniffer)
        if us.isMobileBrowser():
            return True

        return False

    def isCookiedWeb(self):
        """ Check if cookie is set so that mobile browser is forced to
        stay on the web site.
        """
        return self.request.cookies.get(Redirector.COOKIE_NAME) == "web"

    def isMobileWantsWeb(self):
        """
        Mobile site link which ought to force web mode.

        Check "force_web" GET parameter.

        @return True: If stay in web
        """
        return "force_web" in self.request.form

    def getRealContext(self):
        """ Get contentish context for the context.

        Since we are a traversing hook, the context object might be
        bit heterogenous-
        """

        context = aq_inner(self.context)
        return context

        # TODO: Fix this if there are bad pages

        # Crap acquisition magic
        if hasattr(self.context, "aq_parent"):
            return self.context.aq_parent
        else:
            return None  # This context lacks acquisition chain, happens

    def forceWeb(self):
        """
        Set a cookie which forces the mobile browser to stay on the web site.
        """
        response = self.request.response
        response.setCookie(Redirector.COOKIE_NAME, "web", path="/")

    def redirect_url(self, url, query_string,
                     media_type=MobileRequestType.MOBILE):
        """ HTTP redirect to a mobile site matching certain URL.

        @param url: Base URL to rewrite

        @param query_string: Incoming query string on the orignal
            request (for analytics preservation etc.)

        @param media_type: Target media type. "www" or "mobile"

        @return: True if redirect has been made
        """
        context = self.getRealContext()

        location_manager = getMultiAdapter(
            (context, self.request), IMobileSiteLocationManager)

        new_url = location_manager.rewriteURL(url, media_type)
        if url == new_url:
            # No change, so do not redirect, otherwise you go around
            # in circles.
            logger.info('NOT redirecting')
            return False

        if query_string != "":
            new_url += "?" + query_string

        if media_type == MobileRequestType.WEB:
            # Add magical HTTP GET parameter which
            # enforces no redirect cookie

            if query_string == "":
                new_url += "?"
            else:
                new_url += "&"

            new_url += "force_web"

        self.request.response.redirect(new_url)
        # Signal that a redirect has happened
        return True

    def redirect(self, media_type=MobileRequestType.MOBILE):
        """ Redirects to the mobile site staying on the page pointed
        by the current HTTP request.

        Rewrites the current HTTP response.

        @param media_type: Target media type. "www" or "mobile"

        @return: True if redirect has been made
        """

        # This is the serverd URL
        url = self.request["ACTUAL_URL"]

        query_string = self.request["QUERY_STRING"]

        #print "Actual url:" + url
        return bool(self.redirect_url(url, query_string, media_type))

    def intercept(self):
        """ Manage redirects to mobile site.

        @return: True if redirect has been made
        """

        # XXX: Enable this later
        # Abort if gomobile.mobile is not installed
        # - detect by browserlayers.xml
        #if not IGoMobileInstalled.providedBy(self.request):
        #    return False

        # This is needed for templates without views
        context = self.getRealContext()
        if context is None:
            return False

        try:
            getMultiAdapter((context, self.request),
                            IMobileSiteLocationManager)
        except:
            # XXX: gomobile.mobile is not installed.  Should check for
            # IGoMobileInstalled interface, but support is not yet
            # enabled - see intercept()
            return False

        if IApplication.providedBy(context):
            # Do not intercept requests going to the Zope management
            # interface root (one level above Plone sites).
            # Actually, this is not working, as the context is usually
            # <DTMLMethod at /index_html> in that case.
            return False

        discriminator = getUtility(IMobileRequestDiscriminator)
        modes = discriminator.discriminate(context, self.request)

        # Note: just in case redirect logged in users too
        # This might be little stupid and needs to changed later
        is_web = (MobileRequestType.WEB in modes)

        #print "Sniffed: " + str(self.isSniffedMobile())
        #print "Is web:" + str(is_web)
        #print "ModeS:" + str(modes)

        if self.isSniffedMobile() and is_web:

            # Check taht if we are asked to stay on the web site
            if self.isMobileWantsWeb():
                self.forceWeb()
                return False
            elif self.isCookiedWeb():
                return False
            else:
                return bool(self.redirect())

        else:
            # A web browser
            return False


class LoggingRedirector(Redirector):
    """
    A redirector which writes a log entry for every redirect, so that the site
    manager can monitor how much mobile traffic hits the web site.
    """

    def __init__(self, context, request):
        Redirector.__init__(self, context, request)
        self.createLogger()

    def redirect(self):
        self.addLogEntry()
        self.buffer.flush()  # Don't hide data
        return Redirector.redirect(self)

    def createLogger(self):
        """
        """
        # text + append only + no buffering
        self.buffer = open("/tmp/redirect.log", "at", 0)

    def addLogEntry(self):
        """
        """

        date = datetime.now()
        timestamp = str(date)
        user_agent = get_user_agent(self.request)
        page = self.request["ACTUAL_URL"]

        print >> self.buffer, "%s|%s|%s" % (timestamp, page, user_agent)
        print "Redirect log %s|%s|%s" % (timestamp, page, user_agent)
