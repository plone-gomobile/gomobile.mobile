__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, MobileRequestType

class TestDiscriminator(BaseTestCase):

    def afterSetUp(self):
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

        # Reload Plone skins
        self._refreshSkinData()

    def test_is_mobile_request(self):
        """ Check that we can extract width/height from resource based images """

        # By default, we are in web mode
        self.logout()

        self.setDiscriminateMode("web")

        util = getUtility(IMobileRequestDiscriminator)
        flags = util.discriminate(self.portal, self.portal.REQUEST)

        self.assertEqual(len(flags), 1)
        self.assertTrue("web" in flags)

        self.setDiscriminateMode("mobile")
        util = getUtility(IMobileRequestDiscriminator)
        flags = util.discriminate(self.portal, self.portal.REQUEST)
        self.assertEqual(len(flags), 1)
        self.assertTrue("mobile" in flags)

        self.setDiscriminateMode("preview")
        util = getUtility(IMobileRequestDiscriminator)
        flags = util.discriminate(self.portal, self.portal.REQUEST)
        self.assertEqual(len(flags), 2)
        self.assertTrue("mobile" in flags)
        self.assertTrue("preview" in flags)

        self.setDiscriminateMode("admin")
        self.loginAsPortalOwner()
        util = getUtility(IMobileRequestDiscriminator)
        flags = util.discriminate(self.portal, self.portal.REQUEST)
        self.assertEqual(len(flags), 2)
        self.assertTrue("web" in flags)
        self.assertTrue("admin" in flags)


    def test_mobile_tool_traverse(self):

        self.setDiscriminateMode("web")
        tool = self.portal.unrestrictedTraverse("@@mobile_tool")
        self.assertFalse(tool.isMobileRequest())

        # Retraverse since we poke HTTPRequest
        self.setDiscriminateMode("mobile")
        tool = self.portal.unrestrictedTraverse("@@mobile_tool")
        self.assertTrue(tool.isMobileRequest())

    def test_rewrite_url(self):
        """ See that we can present the content URL in different media modes """
        tool = self.portal.unrestrictedTraverse("@@mobile_tool")

        preview = tool.getMobilePreviewURL()

        self.assertTrue("preview." in preview)

        mobile = tool.getMobileSiteURL()
        self.assertTrue("m." in mobile)

        web = tool.getWebSiteURL()
        self.assertTrue(web.startswith("http://nohost"))


    def test_skin_switch(self):
        """ See that correct skin is seleted based on request """


        # TODO: Code this test
        # very difficult to do since,
        # unit tests treat skins differently
        return

        from Products.CMFCore import Skinnable
        # Per-request per thread active skins
        SKINDATA = Skinnable.SKINDATA

        # Assume we have only one thread
        data = SKINDATA.items()[0]

        self.setDiscriminateMode("mobile")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDiscriminator))
    return suite
