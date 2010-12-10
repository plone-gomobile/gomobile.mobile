__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

import utils

@onsetup
def setup_zcml():

    fiveconfigure.debug_mode = True
    import gomobile.convergence
    zcml.load_config('configure.zcml', gomobile.mobile)
    zcml.load_string(utils.ZCML_INSTALL_TEST_DISCRIMINATOR)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('gomobile.mobile')
    ztc.installPackage('gomobiletheme.basic')

# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile', 'gomobiletheme.basic'])

class BaseTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def setUp(self):
        ptc.PloneTestCase.setUp(self)
        utils.modes = ["web"]

    def setDiscriminateMode(self, mode):
        # utils.setDiscriminateMode(self.portal.REQUEST, mode)

        if mode == "preview":
            utils.modes = ["preview", "mobile"]
        elif mode == "admin":
            utils.modes = ["web", "admin"]
        else:
            utils.modes = [mode]

from Products.Five.testbrowser import Browser
from gomobile.mobile.tests.utils import UABrowser

class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """ This is a base class for functional test cases for your custom product.
    """

    def installMobileTheme(self, name):
        """
        This will force Go Mobile Default Theme to be active
        as it seems that if other theme packages are present
        when running tests over many packages,
        the functional test state is not reset between
        packages and we have crap as mobile_properties.mobile_skin name
        instead of Go Mobile Default Theme
        TODO: This could be fixed using test layers?
        """

        qi = self.portal.portal_quickinstaller

        try:
            qi.uninstallProducts([name])
        except:
            pass
        qi.installProduct(name)

    def afterSetUp(self):
        """
        Show errors in console by monkey patching site error_log service
        """

        ptc.FunctionalTestCase.afterSetUp(self)

        self.browser = Browser()
        self.browser.handleErrors = False # Don't get HTTP 500 pages


        self.portal.error_log._ignored_exceptions = ()

        def raising(self, info):
            import traceback
            traceback.print_tb(info[2])
            print info[1]

        from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        SiteErrorLog.raising = raising

        # Hack to fix test running on multiple theme test cases subsequent
        #self.installMobileTheme("Go Mobile Default Theme")
        #self.portal.portal_properties.mobile_properties.mobile_skin = "Go Mobile Default Theme"

        # skin manager must update active skin for the request
        self._refreshSkinData()



    def loginAsAdmin(self):
        """ Perform through-the-web login.

        Simulate going to the login form and logging in.

        We use username and password provided by PloneTestCase.

        This sets session cookie for testbrowser.
        """
        from Products.PloneTestCase.setup import portal_owner, default_password

        # Go admin
        browser = self.browser
        browser.open(self.portal.absolute_url() + "/login_form")
        browser.getControl(name='__ac_name').value = portal_owner
        browser.getControl(name='__ac_password').value = default_password
        browser.getControl(name='submit').click()

    def setUA(self, user_agent, extra_headers=None):
        """
        Create zope.testbrowser Browser with a specific user agent.
        """

        # Be sure to use Products.Five.testbrowser here
        self.browser = UABrowser(user_agent, extra_headers=extra_headers)
        self.browser.handleErrors = False # Don't get HTTP 500 pages

    def setDiscriminateMode(self, mode):
        # utils.setDiscriminateMode(self.portal.REQUEST, mode)

        if mode == "preview":
            utils.modes = ["preview", "mobile"]
        elif mode == "admin":
            utils.modes = ["web", "admin"]
        else:
            utils.modes = [mode]

        # The active skin layers depend on which mode
        # we assume the site is.
        self._refreshSkinData()

