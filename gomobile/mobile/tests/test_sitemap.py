__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"


import unittest
from urllib2 import HTTPError

from zope.component import getUtility, queryUtility, queryMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase
from gomobile.mobile.interfaces import IUserAgentSniffer

from gomobile.mobile.browser.views import FolderListingView

class TestSitemap(BaseFunctionalTestCase):
    """ Test mobile sitemap functions.

    TODO: this do basic code coverage tests and little output validation.
    """

    def afterSetUp(self):

        BaseFunctionalTestCase.afterSetUp(self)

        # Sitemap must be enabled from the settings to access the view
        self.portal.portal_properties.site_properties.enable_sitemap = True


    def test_mobile_sitemap(self):
        """ Check that accuracy of UA match is delivered to us correctly. """

        url = self.portal.absolute_url() + "/@@mobile_sitemap?mode=mobile&language=en&uncompressed"
        self.browser.open(url)
        #print self.browser.contents

        self.assertTrue('xmlns:mobile="http://www.google.com/schemas/sitemap-mobile/1.0"' in self.browser.contents)
        self.assertTrue("<mobile:mobile/>" in self.browser.contents)

    def test_mobile_sitemap_web_mode(self):
        """ Check that accuracy of UA match is delivered to us correctly. """

        url = self.portal.absolute_url() + "/@@mobile_sitemap?language=en&mode=web&uncompressed"
        self.browser.open(url)

        self.assertFalse("mobile:mobile" in self.browser.contents)

    def test_mobile_sitemap_all_languages(self):
        """ Check that accuracy of UA match is delivered to us correctly. """

        url = self.portal.absolute_url() + "/@@mobile_sitemap?mode=mobile&language=ALL"
        self.browser.open(url)

    def test_no_language(self):
        """ Check that language parameter is needed and nothing is executed unless it is given. """

        from urllib2 import HTTPError
        try:
            self.browser.handleErrors = True # Don't get HTTP 500 pages
            url = self.portal.absolute_url() + "/@@mobile_sitemap?mode=mobile"
            self.browser.open(url)
            # should cause HTTPError: HTTP Error 500: Internal Server Error
            raise AssertionError("Should be never reached")
        except HTTPError, e:
            pass

    def test_compressed(self):
        url = self.portal.absolute_url() + "/@@mobile_sitemap?mode=mobile&language=en"
        self.browser.open(url)
        self.assertEqual(self.browser.headers["Content-type"], 'application/octet-stream')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSitemap))
    return suite
