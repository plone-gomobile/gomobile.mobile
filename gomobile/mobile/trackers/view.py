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
    """ Mobile tracking code renderer.

    Can be used stand-alone or from viewlet (see gomobiletheme.basic.viewlets).

    Tracking code can be configured in mobile properties.

    Tracking code can vary based.

    This viewlet is only availble on IMobileLayer.
    If your theme inherits from Plone Mobile theme then this viewlet will be
    enabled for you.
    """
    grok.require('zope2.View')
    grok.context(zope.interface.Interface)

    def getTracker(self, name):
        """ Query mobile tracking backend by name """
        tracker = queryMultiAdapter((self.context, self.request), IMobileTracker, name=name)
        if tracker is None:
            raise RuntimeError("The system does not have tracker registration for %s" % name)

        return tracker

    def update(self, trackingId=None):
        """ Look up tracker and make it generate tracking HTML snippet """
        mobile_properties = getCachedMobileProperties(self.context, self.request)

        if not trackingId:
            trackingId = mobile_properties.tracking_id.strip()

        trackerName = mobile_properties.tracker_name.strip()

        # TODO: Migration hack - may be removed after 1.0 has been released
        debug = getattr(mobile_properties, "tracker_debug", None)

        #print "Tracking:" + str(trackerName)

        if trackingId == "":
            # Assume empty input string equals to not set
            trackingId = None

        if trackerName == "":
            trackerName = None

        if trackerName and trackingId:
            # Look up the tracker
            tracker = self.getTracker(trackerName)
            self.trackingCode = tracker.track(trackingId, debug)

        else:
            self.trackingCode = ""

    def render(self):
        """ Render the HTML snippet """
        # print "Got TC:" + self.trackingCode
        return self.trackingCode

    def __call__(self, trackingId=None):
        self.update(trackingId)
        return self.render()

