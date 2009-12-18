__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator,  MobileRequestType
from gomobile.mobile.behaviors import IMobileBehavior

from gomobile.mobile.browser.views import FolderListingView

class TestHeurestics(BaseTestCase):

    def afterSetUp(self):
        self.number = "+358 123 1234"

        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "Nokia"

    def spoofiPhone(self):
        """
        """
        self.portal.REQUEST.environ["HTTP_USER_AGENT"] = "iPhone"

    def test_normal(self):
        """ In site root, we cannot do mobile folder listing """

        formatter = self.portal.unrestrictedTraverse("@@phone_number_formatter")
        number = formatter.format(self.number)
        self.assertEqual(number, "wtai://wp/mc;+3581231234")


    def test_iphone(self):
        """
        """
        self.spoofiPhone()
        formatter = self.portal.unrestrictedTraverse("@@phone_number_formatter")
        number = formatter.format(self.number)
        self.assertEqual(number, "tel:+3581231234")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHeurestics))
    return suite
