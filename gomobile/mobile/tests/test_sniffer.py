__license__ = "GPL 2"
__copyright__ = "2009-2011 mFabrik Research Oy"

import unittest

from zope.component import getUtility, queryUtility, queryMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.interfaces import IUserAgentSniffer

from gomobile.mobile.browser.views import FolderListingView

ua_nokia_5530 = "Mozilla/5.0 (SymbianOS/9.4; U; Series60/5.0 Nokia5800d-1/21.0.025; Profile/MIDP-2.1 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413"

class TestSniffer(BaseTestCase):
    """ Test UA sniffing functions """

    def test_bad_accuracy(self):
        """ Check that accuracy of UA match is delivered to us correctly. """
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = ua_nokia_5530
        is_mobile = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer).isMobileBrowser()
        self.assertTrue(is_mobile)

    def test_good_accuracy(self):
        """ Check that accuracy of UA match is delivered to us correctly. """
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
        us = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)

        # print "Good mobile accu"
        self.assertTrue(us.isMobileBrowser())

    def test_bad_web_accuracy(self):

        # Some Chrome with made-up version
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/XXX.YY"
        us = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)

        # print "Bad web accu"
        self.assertFalse(us.isMobileBrowser())

    def test_good_web_accuracy(self):
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
        us = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)
        # print "Good web accu"
        self.assertFalse(us.isMobileBrowser())

    def test_web_googlebot(self):
        """
        """
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"
        us = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)
        self.assertFalse(us.isMobileBrowser())

    def test_mobile_googlebot(self):
        """
        """
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
        us = queryMultiAdapter((self.portal, self.portal.REQUEST), IUserAgentSniffer)
        self.assertFalse(us.isMobileBrowser())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSniffer))
    return suite
