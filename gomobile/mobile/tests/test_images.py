__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase, BaseTestCase
from gomobile.mobile.interfaces import IMobileImageProcessor

MOBILE_USER_AGENT="Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN95/11.0.026; Profile MIDP-2.0 Configuration/CLDC-1.1) AppleWebKit/413 (KHTML, like Gecko) Safari/413"


sample1 = """
<p>
<img src="/logo.jpg">
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
    """
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        self.image_processor = getMultiAdapter((self.doc, self.doc.REQUEST), IMobileImageProcessor)
        
    def test_process_html_relative(self):
        """
        """
        result = self.image_processor.processHTML(sample1, True)
        print result

    def test_process_html_portal_root(self):
        """
        """
        result = self.image_processor.processHTML(sample2, True)
        print result
        
    def test_process_html_external(self):
        """
        """
        result = self.image_processor.processHTML(sample3, True)
        print result        
        
class TestResizedView(BaseFunctionalTestCase):
    """ 
    """
    
    def afterSetUp(self):
        BaseFunctionalTestCase.afterSetUp(self)
        self.image_processor = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileImageProcessor)
        
    def checkIsValidDownload(self, url):
        self.browser.open(url)
        ct = self.browser.headers()["content-type"]
        self.assertEqual(ct, )
        
    def test_no_user_agent(self):
        """ Check that redirect does not happen for a normal web browser.
        """
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"auto", "padding_width" : "10"})
        print url
        self.checkIsValidDownload(url)
        
        
    def checkIsUnauthorized(self, url):
        self.checkIsValidDownload(url)
        
        
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
        self.checkIsValidDownload(url)

    def test_invalid_width_high(self):
        url = self.image_processor.getImageDownloadURL("/logo.jpg", {"width":"1200", "padding_width" : "10"})
        self.checkIsValidDownload(url)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProcessHTML))
    suite.addTest(unittest.makeSuite(TestResizedView))
    return suite
