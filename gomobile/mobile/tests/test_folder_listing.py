__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator,  MobileRequestType
from gomobile.mobile.behaviors import IMobileBehavior

from gomobile.mobile.browser.views import FolderListingView

class TestFolderListing(BaseTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        # Reload Plone skins
        self._refreshSkinData()

        self.loginAsPortalOwner()

        self.portal.invokeFactory("Folder", "folder")
        self.portal.folder.invokeFactory("Document", "doc")
        self.portal.folder.invokeFactory("Document", "doc2")

        self.spoofActiveTemplate("some_view_not_blacklisted")

    def spoofActiveTemplate(self, viewName):
        """ We cannot do unit testing because FolderListingView.getActiveTemple()
        does not provide a template which would allow listing.

        """

        # Monkey-patch for tests
        def dummy(self):
            return viewName

        old = FolderListingView.getActiveTemplate
        FolderListingView.getActiveTemplate = dummy

    def getItems(self, context):
        """ Perform mobile folder listing.
        """
        view = context.restrictedTraverse("@@mobile_folder_listing")
        return view.getItems()

    def test_site_root(self):
        """ In site root, we cannot do mobile folder listing """
        self.assertEqual(len(self.getItems(self.portal)), 0)

    def test_normal_listing(self):
        """
        """
        items = self.getItems(self.portal.folder)
        self.assertEqual(len(items), 2)

    def test_not_appear_in_listing(self):
        """
        Check that mobile behavior prevents items to appear in the listing.
        """
        behavior = IMobileBehavior(self.portal.folder.doc2)
        behavior.appearInFolderListing = False
        behavior.save()

        # self.assertEqual(self.getItems(self.portal.folder), None)
        items = self.getItems(self.portal.folder)
        self.assertEqual(len(self.getItems(self.portal.folder)), 1)


    def test_view_does_not_allow_automatic_listing(self):
        """ Try behavior properties """

        self.spoofActiveTemplate("folder_listing")
        items = self.getItems(self.folder)
        self.assertEqual(len(items), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFolderListing))
    return suite
