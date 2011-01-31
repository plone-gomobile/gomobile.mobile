"""

    Check that the site is clean after uninstall.

"""

__license__ = "GPL 2"
__copyright__ = "2009-2011 mFabrik Research Oy"

import unittest

from zope.component import getUtility, queryUtility, queryMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.behaviors import IMobileBehavior, mobile_behavior_factory,  MobileBehaviorStorage

from zope.annotation.interfaces import IAnnotations

class TestUninstall(BaseTestCase):
    """ Test UA sniffing functions """
    
    
    def make_some_evil_site_content(self):
        """
        Add annotations etc. around the site
        """

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc

        behavior = IMobileBehavior(doc)
        behavior.mobileFolderListing = False
        behavior.save()
        
        annotations = IAnnotations(doc)
        
    def uninstall(self, name="gomobile.mobile"):
        qi = self.portal.portal_quickinstaller
        
        try:
            qi.uninstallProducts([name])
        except:
            pass
        qi.installProduct(name)        
    
    def test_annotations(self):
        """ Check that uninstaller cleans up annotations from the docs
        """
        self.make_some_evil_site_content()
        self.uninstall()
        
        annotations = IAnnotations(self.portal.doc)
        self.assertFalse("mobile" in annotations)
        
        
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUninstall))
    return suite
