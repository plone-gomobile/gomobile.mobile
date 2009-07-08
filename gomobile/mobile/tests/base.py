__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

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
    zcml.load_config('configure.zcml', gomobile.convergence)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.

    ztc.installPackage('gomobile.mobile')    
    #ztc.installPackage('gomobile.convergence')

    
    
# The order here is important.
setup_zcml()
ptc.setupPloneSite(products=['gomobile.mobile'])

class BaseTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    
    def setUp(self):
        ptc.PloneTestCase.setUp(self)     
        
    def setDiscriminateMode(self, mode):
        utils.setDiscriminateMode(self.portal.REQUEST, mode)
