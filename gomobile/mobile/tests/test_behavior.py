__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import unittest

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileContentish

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.behaviors import IMobileBehavior, mobile_behavior_factory,  MobileBehaviorStorage

from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import WrongType

class TestBehavior(BaseTestCase):

    def make_behavor_persistent(self, behavior):
        mobile_behavior_factory.makePersistent(behavior)

    def test_has_behavior(self):
        """ Test behavior and assignable works nicely.
        """

        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc

        # Check assignable works
        from plone.behavior.interfaces import IBehaviorAssignable
        assignable = IBehaviorAssignable(doc, None)

        self.assertTrue(assignable.supports(IMobileBehavior))
        self.assertNotEqual(assignable, None)


        # Check behavior works
        self.assertTrue(IMobileContentish.providedBy(doc))
        behavior = IMobileBehavior(doc)

        self.assertNotEquals(behavior, None)

    def test_setter(self):
        """ Try behavior properties """
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc

        self.assertTrue(IMobileContentish.providedBy(doc))
        behavior = IMobileBehavior(doc)

        self.assertTrue(isinstance(behavior, MobileBehaviorStorage))
        self.assertEqual(behavior.mobileFolderListing, True)

        behavior.mobileFolderListing = False


    def test_check_registration(self):
        """ Check that our behavior is correctly adapting
        """

        from zope.component import getGlobalSiteManager
        sm = getGlobalSiteManager()

        registrations = [a for a in sm.registeredAdapters() if a.provided == IMobileBehavior ]
        self.assertEqual(len(registrations), 1)


    def test_shit_input(self):
        """ Try put in bad data """


        self.loginAsPortalOwner()
        self.portal.invokeFactory("Document", "doc")
        doc = self.portal.doc
        behavior = IMobileBehavior(doc)

        try:
            behavior.mobileFolderListing = "xxx"
            raise AssertionError("Should not be never reached")
        except WrongType:
            pass

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBehavior))
    return suite
