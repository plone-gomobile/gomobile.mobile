"""

    Mobile site testing utils

   These are in separate file, so that third party products can use them easily.
"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import zope.interface

from gomobile.mobile.locationmanager import DomainNameBasedMobileSiteLocationManager
from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType

def setDiscriminateMode(request, mode):
    """ Spoof the media discrimination mode for unit tests.

    NOTE: Does not work in functional tests.

    Poke HTTP request internals to look like it is directed
    to domain name based discriminating.

    @param mode: 'mobile' or 'web'
    """

    def setURL(url):
        request.other["URL"] = url
        request.other["ACTUAL_URL"] = url
        request.other["SERVER_URL"] = url

    if mode == "mobile":
        host = "mobile.nohost"
    elif mode == "preview":
        host = "preview.nohost"
    elif mode == "web":
        host = "web.nohost"
    else:
        raise RuntimeError("Unknown mode:" + mode)

    setURL("http://" + host)
    request.environ["HTTP_HOST"] = host


class TestMobileRequestDiscriminator(object):
    """ Spoof HTTP request media type for Zope test browser.

    How to activate for functional tests::

        from gomobile.mobile.tests.utils import TestMobileRequestDiscriminator


        # ZCML to override media discriminator with test stub
        ZCML_FIXES='''
        <configure
            xmlns="http://namespaces.zope.org/zope">
         <utility
             provides="gomobile.mobile.interfaces.IMobileRequestDiscriminator"
             factory="gomobile.mobile.tests.utils.TestMobileRequestDiscriminator" />
        </configure>
        '''


        @onsetup
        def setup_zcml():
            ...
            zcml.load_string(ZCML_FIXES)

        class ThemeTestCase(BaseTestCase):


        def setDiscriminateMode(self, mode):
            '''
            Spoof the following HTTP request media.

            @param: "mobile", "web" or other MobileRequestType pseudo-constant
            '''
            TestMobileRequestDiscriminator.modes = [mode]
    """

    zope.interface.implements(IMobileRequestDiscriminator)

    modes = [MobileRequestType.MOBILE]

    def discriminate(self, context, request):
        return TestMobileRequestDiscriminator.modes