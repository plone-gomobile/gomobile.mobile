__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest
import zope.event

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase, BaseTestCase

class TestContentType(BaseFunctionalTestCase):
    """ Check that the content type is detected correctly for mobile.
    """

    def test_content_type(self):
        """ Check that content type is something all mobile phones agree on.
        """
        
        # not being called
        self.setDiscriminateMode("mobile")
        #self.browser.open(self.portal.absolute_url())
        
        response = self.portal.REQUEST.response
        response.setHeader("Content-type", "text/html")
        
        # Manually trigger content type code as postpublicationhook is unsupported by zope.testbrowser
        from plone.postpublicationhook.event import AfterPublicationEvent
                
        event = AfterPublicationEvent(self.portal, self.portal.REQUEST)
        zope.event.notify(event)
        
        #self.assertTrue(response.getHeader("content-type").startswith("Content-Type: application/xhtml+xml"))
        ct = response.getHeader("content-type")
        self.assertTrue(ct.startswith("text/html"), "Got:" + str(ct))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestContentType))
    return suite
