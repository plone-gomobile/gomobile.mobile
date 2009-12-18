__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, MobileRequestType, IMobileRedirector, IUserAgentSniffer



class TestRedirector(BaseTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

    def set_user_agent(self, mode):
        """
        """
        if mode == "web":
            self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Foobar"
        else:
            self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413"
            ua = getMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)
            # This attribute is supported by pywurlf only
            import pdb ; pdb.set_trace()
            self.assertTrue(ua.get("is_wireless_device"))

    def test_redirect_web_browser(self):
        self.set_user_agent("web")
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), name="mobile_redirector")
        self.assertEqual(redirector.intercept(), False)

    def test_redirect_mobile_browser(self):
        self.set_user_agent("mobile")
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), False)

    def test_redirect_mobile_browser_force_web(self):
        self.set_user_agent("mobile")
        self.portal.REQUEST.form["forceweb"] = True
        redirector = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileRedirector)
        self.assertEqual(redirector.intercept(), False)

        # Check that cookie was set
        response = self.portal.REQUEST.response
        import pdb ; pdb.set_trace()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRedirector))
    return suite
