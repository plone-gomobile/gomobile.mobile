__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import random

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    site = context.getSite()
    
    # Reseed mobile image resizer secret
    site.portal_properties.mobile_properties.image_resizer_secret = str(random.randint(0, 999999999))
