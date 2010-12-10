"""

    Default user-agent sniffing information based on mobile.sniffer and wurlf products.

    Wurlf database is supplied with pywurlf package.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import logging

import zope.interface
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger("Plone")

from mobile.sniffer.detect import  detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent

try:
    from mobile.sniffer.wurlf.sniffer import WurlfSniffer

    # Wrapper sniffer instance
    # All start-up delay goes on this line
    _sniffer = WurlfSniffer()
except ImportError, e:
    import traceback
    traceback.print_exc()
    logger.exception(e)
    logger.error("Could not import Wurlf sniffer... add pywurfl and python-Lehvenstein to buildout.cfg eggs section")
    _sniffer = None

# Annotations cache key
KEY = "sniffer_user_agent"


class SessionCachedUASniffer(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def isMobileBrowser(self):
        ua = get_user_agent(self.request)
        if ua:
            return detect_mobile_browser(ua)
        else:
            # User agent missing from HTTP request
            return False

    def getUserAgentRecord(self):
        """ Resolve user-agent record for the request.

        User agent look-up may be expensive.
        Store cached value on the request object itself and
        session.

        @return: mobile.sniffer.base.UserAgent instance or None if no user agent found or it cannot be looked up
        """

        context = self.context
        request = self.request

        if _sniffer == None:
            # For some reason, coudln't initialize
            # print "No sniffer"
            return None

        # First check if we have cached hit on HTTP request
        annotations = IAnnotations(request)
        ua = annotations.get(KEY, None)

        if context == None:
            # TODO: Not sure yet when this hpapens,
            # but it does
            logger.warn("No context for user agent sniffing")
            ua = _sniffer.sniff(request)
            return ua

        site = context.portal_url.getPortalObject()

        if "session_data_manager" in site:
            sdm = site["session_data_manager"]
        else:
            sdm = None

        # Then check if we have cached hit on session
        if not ua:
            # Session data manager is not availabe in unit tests
            if sdm != None:
                session = sdm.getSessionData(create=True)
                ua = session.get(KEY, None)

        if not ua:

            ua = _sniffer.sniff(request)
            # print "Sniffed:" + str(ua)

            # TODO: Session based caching is disabled for now,
            # as pywurfl objects are not pickable

            # Session set may start transaction
            # Is this too expensive?
            if ua:
                if sdm != None:
                    session = sdm.getSessionData(create=True)
                    session.set(KEY, ua)

            # session.set(KEY, ua)

        annotations[KEY] = ua

        return ua

