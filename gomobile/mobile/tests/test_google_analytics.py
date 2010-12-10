"""

    Please see also functional tests in gomobiletheme.basic product.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"


import unittest

from zope.component import getUtility, queryUtility, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.tests.base import BaseTestCase, BaseFunctionalTestCase
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator,  MobileRequestType, IMobileTracker


class TestGoogleAnalytics(BaseTestCase):
    """
    Test case for GA tracker.
    """

    def afterSetUp(self):

        BaseTestCase.afterSetUp(self)

        self.portal.portal_properties.mobile_properties.tracker_name = "google-mobile"

        # This id is updated in GA, manually check whether it gets hits or no
        self.portal.portal_properties.mobile_properties.tracking_id = "MO-8819100-7"

    def test_normal(self):
        """ Calls tracker code renderer.

        Assume GA tracking code is rendered, by having the setup above.
        """


        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="mobiletracker")
        code = view()
        self.assertTrue("MO-" in code)

        # NOTE: Manually checked whether tracker statistics have been updated


    def test_javascript(self):
        """ Test presence of Javascript based tracking.

        """

        self.portal.portal_properties.mobile_properties.tracker_name = "google-web"

        # This id is updated in GA, manually check whether it gets hits or no
        self.portal.portal_properties.mobile_properties.tracking_id = "UA-8819100-7"


        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="mobiletracker")
        code = view()
        self.assertTrue("UA-" in code)

        # NOTE: Manually checked whether tracker statistics have been updated


    def test_bad_tracker_id(self):
        """
        GA ids must be MO-xxx
        """

        self.portal.portal_properties.mobile_properties.tracking_id = "UA-8819100-7"

        from gomobile.mobile.trackers.ga import BadTrackerId
        try:
            view = getMultiAdapter((self.portal, self.portal.REQUEST), name="mobiletracker")
            code = view()
            raise AssertionError("No dice")
        except BadTrackerId, e:
            pass



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestGoogleAnalytics))
    return suite

