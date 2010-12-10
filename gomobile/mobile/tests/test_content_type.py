"""

    Content type and docstring mangling unit tests.


"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"


import unittest
import zope.event

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseFunctionalTestCase, BaseTestCase
from gomobile.mobile.tests.utils import GOOGLEBOT_MOBILE_USER_AGENT, UABrowser

MOBILE_DOCTYPE = '<?xml version="1.0" encoding="utf-8" ?><!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">'

class TestMobileContentType(BaseFunctionalTestCase):
    """ Check that the content type is detected correctly for mobile.

    NOTE: Zope testbrowser does not support post-publication hook,
    thus we call it manually.
    """



    def test_content_type(self):
        """ Check that content type is something all mobile phones agree on.
        """

        # not being called
        self.setDiscriminateMode("mobile")

        # Construct a faux response as text/html payload
        response = self.portal.REQUEST.response
        response.setHeader("Content-type", "text/html")

        # Manually trigger content type code as postpublicationhook is unsupported by zope.testbrowser
        from plone.postpublicationhook.event import AfterPublicationEvent

        event = AfterPublicationEvent(self.portal, self.portal.REQUEST)
        zope.event.notify(event)

        #self.assertTrue(response.getHeader("content-type").startswith("Content-Type: application/xhtml+xml"))
        ct = response.getHeader("content-type")
        self.assertTrue(ct.startswith("text/html"), "Got:" + str(ct))

    def test_content_type_accept_xml(self):
        """ Check that user agent which accepts XHTML, but is not bot, gets normal HTML headers.
        """

        self.setDiscriminateMode("mobile")

        self.portal.REQUEST.environ["HTTP_ACCEPT"] = "application/xhtml+xml"

        # Construct a faux response as text/html payload
        response = self.portal.REQUEST.response
        response.setHeader("Content-type", "text/html")

        # Manually trigger content type code as postpublicationhook is unsupported by zope.testbrowser
        from plone.postpublicationhook.event import AfterPublicationEvent

        event = AfterPublicationEvent(self.portal, self.portal.REQUEST)
        zope.event.notify(event)

        #self.assertTrue(response.getHeader("content-type").startswith("Content-Type: application/xhtml+xml"))
        ct = response.getHeader("content-type")
        self.assertTrue(ct.startswith("text/html"), "Got:" + str(ct))


    def test_googlebot(self):
        """
        Test rewriting of
        """
        self.setDiscriminateMode("mobile")

        self.portal.REQUEST.environ["HTTP_ACCEPT"] = "application/xhtml+xml"
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = GOOGLEBOT_MOBILE_USER_AGENT

        # Construct a faux response as text/html payload
        response = self.portal.REQUEST.response
        response.setHeader("Content-type", "text/html")

        # Manually trigger content type code as postpublicationhook is unsupported by zope.testbrowser
        from plone.postpublicationhook.event import AfterPublicationEvent

        event = AfterPublicationEvent(self.portal, self.portal.REQUEST)
        zope.event.notify(event)

        #self.assertTrue(response.getHeader("content-type").startswith("Content-Type: application/xhtml+xml"))
        ct = response.getHeader("content-type")
        self.assertTrue(ct.startswith("application/xhtml+xml"), "Got:" + str(ct))

    def test_googlebot_doctype(self):
        """ Check that mobile bot gets correct XHTML mobile doctype string.

        """
        self.setDiscriminateMode("mobile")
        self.setUA(GOOGLEBOT_MOBILE_USER_AGENT, extra_headers=[("ACCEPT", "application/xhtml+xml")])

        self.browser.open(self.portal.absolute_url())

        html = self.browser.contents

        slice = html[0:len(MOBILE_DOCTYPE)]

        # Eyeball comparison
        print slice
        #print MOBILE_DOCTYPE


        # Check that content type is correct
        self.assertTrue(html.startswith(MOBILE_DOCTYPE), "Got:" + str(html[0:200]))


    def test_check_valid_xml(self):
        """ Check that front page content is valid XML """


        self.setDiscriminateMode("mobile")
        self.setUA(GOOGLEBOT_MOBILE_USER_AGENT, extra_headers=[("ACCEPT", "application/xhtml+xml")])

        self.browser.open(self.portal.absolute_url())

        html = self.browser.contents

        from lxml import etree

        print "Got front page:" + html

        # Assert no exception is risen
        root = etree.fromstring(html)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMobileContentType))
    return suite
