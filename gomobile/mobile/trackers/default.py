"""

   Use same tracking code from the web site in mobile.

"""

try:
    # Python >= 2.5
    from hashlib import md5
except ImportError:
    # Python < 2.5
    from md5 import md5

import zope.interface

from gomobile.mobile.interfaces import IMobileTracker

class PloneDefaultTracker(object):
    """ Google Analytics mobile analytics tracker abstraction.

    Uses __utm.gif synchronous server calling for the visitor tracking.
    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId, debug):
        # use default plone tracker viewlet to render the tracking code
        code = self.context.unrestrictedTraverse("@@viewlets/plone.analytics")
        return code

