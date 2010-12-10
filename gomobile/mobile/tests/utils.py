"""

    Mobile site testing utils

   These are in separate file, so that third party products can use them easily.
"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import zope.interface

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType
from gomobile.mobile.browser.views import FolderListingView

MOBILE_USER_AGENT="Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413"

HIGHEND_MOBILE_USER_AGENT="Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"

GOOGLEBOT_MOBILE_USER_AGENT = "SAMSUNG-SGH-E250/1.0 Profile/MIDP-2.0 Configuration/CLDC-1.1 UP.Browser/6.2.3.3.c.1.101 (GUI) MMP/2.0 (compatible; googlebot-mobile/2.1; +http://www.google.com/bot.html)"


def setDiscriminateMode(request, mode):
    """ Spoof the media discrimination mode for unit tests.

    NOTE: Does not work in functional tests.

    Poke HTTP request internals to look like it is directed
    to domain name based discriminating.

    @param mode: 'mobile' or 'web'
    """

    def setURL(url):
        request.other["URL"] = url
        request.other["ACTUAL_URL"] = url
        request.other["SERVER_URL"] = url

    if mode == "mobile":
        host = "mobile.nohost"
    elif mode == "preview":
        host = "preview.nohost"
    elif mode == "web":
        host = "web.nohost"
    else:
        raise RuntimeError("Unknown mode:" + mode)

    setURL("http://" + host)
    request.environ["HTTP_HOST"] = host


# Mock variable which can be manipulated by unit tests
# This must be web by default or unit test bootstrap code (skin installation) does not work
modes = [MobileRequestType.WEB]

ZCML_INSTALL_TEST_DISCRIMINATOR='''
        <configure
            xmlns="http://namespaces.zope.org/zope">
         <utility
             provides="gomobile.mobile.interfaces.IMobileRequestDiscriminator"
             factory="gomobile.mobile.tests.utils.TestMobileRequestDiscriminator" />
        </configure>
        '''


class TestMobileRequestDiscriminator(object):
    """ Spoof HTTP request media type for Zope test browser.

    How to activate for functional tests::

        from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator


        # ZCML to override media discriminator with test stub
        ZCML_FIXES='''
        <configure
            xmlns="http://namespaces.zope.org/zope">
         <utility
             provides="gomobile.mobile.interfaces.IMobileRequestDiscriminator"
             factory="gomobile.mobile.tests.utils.TestMobileRequestDiscriminator" />
        </configure>
        '''


        @onsetup
        def setup_zcml():
            ...
            zcml.load_string(ZCML_FIXES)

        class ThemeTestCase(BaseTestCase):


        def setDiscriminateMode(self, mode):
            '''
            Spoof the following HTTP request media.

            @param: "mobile", "web" or other MobileRequestType pseudo-constant
            '''
            TestMobileRequestDiscriminator.modes = [mode]
    """

    zope.interface.implements(IMobileRequestDiscriminator)

    @staticmethod
    def setModes(_modes):
        global modes
        modes = _modes

    def discriminate(self, context, request):
        global modes
        return modes

def spoofMobileFolderListingActiveTemplate(viewName="something"):
    """ Make sure that mobile folder listing "active template" check is turned off.

    Otherwise unit tests will always use "folder_listing" template which is blacklisted.
    """

    # Monkey-patch for tests
    def dummy(self):
        return viewName

    old = FolderListingView.getActiveTemplate
    FolderListingView.getActiveTemplate = dummy


from zope.testbrowser import browser
from Products.Five.testbrowser import PublisherHTTPHandler
from Products.Five.testbrowser import PublisherMechanizeBrowser

class UABrowser(browser.Browser):
    """A Zope ``testbrowser` Browser that uses the Zope Publisher.

    The instance must set a custom user agent string.
    """

    def __init__(self, user_agent, url=None, extra_headers=None):
        """

        @param user_agent: HTTP_USER_AGENT string to use

        @param extra_headers: List of HTTP header tuples
        """

        mech_browser = PublisherMechanizeBrowser()
        mech_browser.addheaders = [("User-agent", user_agent),]

        if extra_headers:
             mech_browser.addheaders += extra_headers

        # override the http handler class
        mech_browser.handler_classes["http"] = PublisherHTTPHandler
        browser.Browser.__init__(self, url=url, mech_browser=mech_browser)




