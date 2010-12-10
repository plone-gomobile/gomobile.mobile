__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from AccessControl import Unauthorized
from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase, BaseTestCase
from gomobile.mobile.interfaces import IMobileImageProcessor

from gomobile.mobile.tests.utils import MOBILE_USER_AGENT

sample1 = """
<p>
<img src="logo.jpg">
</p>
"""

sample2 = """
<p>
<img src="/logo.jpg">
</p>
"""


sample3 = """
<p>
<img src="http://plone.org/logo.jpg">
</p>
"""

class TestProcessHTML(BaseTestCase):
    """
    Test content HTML rewriting for resized images.

    TODO: Needs lots of more cases covered here.
    """
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        self.image_processor = getMultiAdapter((self.doc, self.doc.REQUEST), IMobileImageProcessor)

    def test_process_html_relative(self):
        """ Check that exceptions don't fly

        TODO: Something smarter here
        """
        result = self.image_processor.processHTML(sample1, True)
        # print "1:" + result
        self.assertTrue("float: none" in result)
        # Relative to the site root
        self.assertTrue("url=logo.jpg" in result)


    def test_process_html_portal_root(self):
        """ Check that exceptions don't fly

        TODO: Something smarter here
        """
        result = self.image_processor.processHTML(sample2, True)
        self.assertTrue("float: none" in result)
        # Relative to the site root
        self.assertTrue("url=logo.jpg" in result)

    def test_process_html_external(self):
        """ Check that exceptions don't fly

        TODO: Something smarter here
        """

        result = self.image_processor.processHTML(sample3, True)
        #print "3:" + result
        self.assertTrue("float: none" in result)
        self.assertTrue("url=http%3A%2F%2Fplone.org%2Flogo.jpg" in result)


class TestResizedView(BaseFunctionalTestCase):
    """ Test mobile image resizer.

    This stressed the view which performs the actual image scale down and result caching.
    """

    def afterSetUp(self):
        BaseFunctionalTestCase.afterSetUp(self)
        self.image_processor = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileImageProcessor)

        self.image_processor.init()
        self.image_processor.cache.invalidate()

    def checkIsValidDownload(self, url):
        """
        Check whether we generated good image response.
        """
        self.browser.open(url)
        ct = self.browser.headers["content-type"]
        self.assertEqual(ct, "image/jpeg", "got:" + ct)

    def test_no_user_agent(self):
        """ Check that redirect does not happen for a normal web browser.
        """
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "10"})
        # print url
        self.checkIsValidDownload(url)


    def checkIsUnauthorized(self, url):
        """
        Check whether URL gives Unauthorized response.
        """

        import urllib2

        # Disable redirect on security error
        self.portal.acl_users.credentials_cookie_auth.login_path = ""

        # Unfuse exception tracking for debugging
        # as set up in afterSetUp()
        self.browser.handleErrors = True


        # Comment out these to make 500 exceptions visible
        def raising(self, info):
            pass
        self.portal.error_log._ignored_exceptions = ("Unauthorized")
        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising
        ## here

        try:
            self.browser.open(url)
            raise AssertionError("No Unauthorized risen:" + url)
        except urllib2.HTTPError,  e:
            # Mechanize, the engine under testbrowser
            # uses urlllib2 and will raise this exception
            self.assertEqual(e.code, 401, "Got HTTP response code:" + str(e.code))

    def test_is_cached(self):

        from gomobile.mobile.browser import imageprocessor
        imageprocessor.cache_hits = 0

        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "10"})
        self.checkIsValidDownload(url)

        self.assertEqual(imageprocessor.cache_hits, 0)

        # Now the same URL should be cached hit
        self.checkIsValidDownload(url)
        self.assertEqual(imageprocessor.cache_hits, 1)

        # Change some parameters and see that we are not cached anymore
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "20"})
        self.checkIsValidDownload(url)
        self.assertEqual(imageprocessor.cache_hits, 1)

    def test_relative(self):
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "10"})
        self.checkIsValidDownload(url)

    def test_external(self):
        url = self.image_processor.getImageDownloadURL("http://plone.org/logo.jpg", {"width":"auto", "padding_width" : "10"})
        self.checkIsValidDownload(url)

    def test_invalid_width_low(self):
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"0", "padding_width" : "10"})


        # print url
        #import pdb ; pdb.set_trace()
        self.checkIsUnauthorized(url)

    def test_invalid_width_high(self):
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"1200", "padding_width" : "10"})
        self.checkIsUnauthorized(url)

    def test_clear_cache(self):
        secret = self.image_processor.getSecret()
        url = self.portal.absolute_url() + "/@@mobile_image_processor_clear_cache?secret=" + secret
        self.browser.open(url)

    def test_clear_cache_bad_secret(self):
        url = self.portal.absolute_url() + "/@@mobile_image_processor_clear_cache?secret=abc"
        self.checkIsUnauthorized(url)

    def test_bad_secret(self):
        """
        Check that we need to have image processor view query parameters signed correctly or
        will get Unauthorized.
        """
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "10"})
        # remove secret paramater
        url = url.replace("secret", "notsecret")
        self.checkIsUnauthorized(url)


class TestDocWithImage(BaseFunctionalTestCase):
    """ Check that we transform document body text properly for mobile.

     .. warning ::

         As these tests depend on skin layers, they have been moved to gomobiletheme.basic
         package.
    """

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProcessHTML))
    suite.addTest(unittest.makeSuite(TestResizedView))
    return suite
