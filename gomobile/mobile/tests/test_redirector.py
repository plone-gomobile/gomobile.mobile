__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase, BaseTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, MobileRequestType, IMobileRedirector, IUserAgentSniffer

MOBILE_USER_AGENT="Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413"

class TestRedirector(BaseTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

    def set_user_agent(self, mode):
        """
        """
        if mode == "web":
            self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)"
        else:
            self.portal.REQUEST.environ["HTTP_USER_AGENT"] = MOBILE_USER_AGENT
            mobile = getMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer).isMobileBrowser()
            # This attribute is supported by pywurlf only
            self.assertTrue(mobile)

    def test_redirect_web_browser(self):
        self.set_user_agent("web")
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), False)

    def test_redirect_mobile_browser(self):
        self.set_user_agent("mobile")
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), True)

    def test_redirect_mobile_browser_force_web(self):
        self.set_user_agent("mobile")
        self.portal.REQUEST.form["force_web"] = True
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), False)

        # Check that cookie was set
        response = self.portal.REQUEST.response
        cookies = response._cookie_list()
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0], 'Set-Cookie: mobile_mode="web"; Path=/')

    def test_redirect_mobile_browser_web_cookie_set(self):
        self.set_user_agent("mobile")
        self.portal.REQUEST.cookies["mobile_mode"] = "web"
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), False)


class TestRedirectorFunctionality(BaseFunctionalTestCase):
    """ Check that mobile redirect hook is effective.

    XXX: Must be manually tested as zope.testbrowser does not support
    postpublication hook.
    """

    def xxx_test_no_mobile(self):
        """ Check that redirect does not happen for a normal web browser.
        """
        self.browser.open(self.portal.absolute_url())
        self.assertEqual(self.browser.headers["Status"], "200 Ok")
        #self.assertEqual(self.browser.cookies.get("mobile_mode", None), None)

    def xxx_test_redirect_mobile(self):
        """ Check that we got redirect to mobile site if we pose mobile user agent.
        """

        self.setUA(MOBILE_USER_AGENT)
        self.browser.open(self.portal.absolute_url())

        # Check that we got redirect and the site is right
        self.assertEqual(self.browser.headers["Status"], "302")
        self.assertEqual(self.browser.cookies["mobile_mode"], "mobile")
        self.assertEqual(self.browser.contents, "")
        # Check that we got redirect to mobile site

        # Now try to come back (follow Go to web site link)
        self.browser.open(self.portal.absolute_url() + "?force_web")
        self.assertEqual(self.browser.headers["Status"], "200")
        self.assertEqual(self.browser.cookies["mobile_mode"], "web")

        # Check that our cookie statys
        self.browser.open(self.portal.absolute_url())
        self.assertEqual(self.browser.headers["Status"], "200")
        self.assertEqual(self.browser.cookies["mobile_mode"], "web")



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRedirector))
    suite.addTest(unittest.makeSuite(TestRedirectorFunctionality))
    return suite
