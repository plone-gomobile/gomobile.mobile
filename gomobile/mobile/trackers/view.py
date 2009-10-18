"""

    Default tracker renderer.


"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"


import zope.interface
from zope.component import getMultiAdapter, queryMultiAdapter

from gomobile.mobile.utilities import getCachedMobileProperties
from gomobile.mobile.interfaces import IMobileTracker

from five import grok

class MobileTracker(grok.CodeView):
    """ Insert tracking code to a page.

    Tracking code can be configured in mobile properties.

    Tracking code can vary based.

    This viewlet is only availble on IMobileLayer.
    If your theme inherits from Plone Mobile theme then this viewlet will be
    enabled for you.
    """
    grok.require('zope2.View')
    grok.context(zope.interface.Interface)

    def getTracker(self, name):
        tracker = queryMultiAdapter((self.context, self.request), IMobileTracker, name=name)
        if tracker is None:
            raise RuntimeError("The system does not have tracker registration for %s" % name)

        return tracker

    def update(self):

        mobile_properties = getCachedMobileProperties(self.context, self.request)

        self.trackingId = mobile_properties.tracking_id.strip()

        self.trackerName = mobile_properties.tracker_name.strip()

        if self.trackingId == "":
            # Assume empty input string equals to not set
            self.trackingId = None

        if self.trackerName == "":
            self.trackerName = None

        if self.trackerName and self.trackingId:
            # Look up the tracker
            tracker = getTracker(self.trackerName)
            self.trackingCode = tracker.track(self.trackingId)

        else:
            self.trackingCode = ""

    def render(self):
        return self.trackingCode

    def __call__(self):
        self.update()
        return self.render()

