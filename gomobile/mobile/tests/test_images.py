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

    def test_process_html_portal_root(self):
        """
        """
        result = self.image_processor.processHTML(sample2, True)

    def test_process_html_external(self):
        """
        """
        result = self.image_processor.processHTML(sample3, True)
                
        
class TestResizedView(BaseFunctionalTestCase):
    """ 
    """
    
    def afterSetUp(self):
        self.image_processor = getMultiAdapter((self.portal, self.portal.REQUEST), IMobileImageProcessor)
        
    def test_no_user_agent(self):
        """ Check that redirect does not happen for a normal web browser.
        """



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProcessHTML))
    #suite.addTest(unittest.makeSuite(TestRedirectorFunctionality))
    return suite
