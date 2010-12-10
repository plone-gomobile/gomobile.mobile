__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import os, sys
import unittest
from gomobile.mobile.tests.base import BaseTestCase

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.browser import resizer


class TestMobileImages(BaseTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        # Reload Plone skins
        self._refreshSkinData()

        # Upload an AT field based image
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Image", "test_img")

        path = os.path.dirname(sys.modules[__name__].__file__)
        path = os.path.join(path, "logo.jpg")

        f = open(path)
        #f.filename  = path
        portal = self.portal
        self.portal.test_img.setImage(f)
        f.close()
        self.logout()

    def runResize(self, img):
        """

        @param img: Traversing path to the image
        """
        request = self.portal.REQUEST
        query = resizer.getResizedImageQuery(path=img, width=10, height=10)

        for key, val in query.items():
            request.set(key, val)

        view = self.portal.restrictedTraverse("@@mobile_image_resizer")

        output = view()


    def test_res_info(self):
        """ Check that we can extract width/height from resource based images """
        img  = "++resource++gomobile.mobile/phone_back.png"
        portal = self.portal
        img_obj = portal.unrestrictedTraverse(img)


    def test_skin_info(self):
        """ Check that we can extract width/height from Zope skin layer based images """
        portal = self.portal
        img = "logo.jpg"
        img_obj = portal.unrestrictedTraverse(img)


    def test_res_resizer(self):
        img  = "++resource++gomobile.mobile/phone_back.png"
        self.runResize(img)

    def test_skin_resizer(self):
        img  = "logo.jpg"
        self.runResize(img)

    def test_at_resizer(self):
        img  = "test_img/getImage"
        self.runResize(img)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMobileImages))
    return suite
