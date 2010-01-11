__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import random

from plone.browserlayer.utils import unregister_layer

def fix_browserlayer(site):
    """
    This was not properly done before 1.0 using theme layers. There might be corrupted registry on old sites. 
    """
    try:
        unregister_layer("gomobile.mobile")
    except KeyError:
        pass

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    site = context.getSite()
    
    # Reseed mobile image resizer secret
    site.portal_properties.mobile_properties.image_resizer_secret = str(random.randint(0, 999999999))


    fix_browserlayer(site)