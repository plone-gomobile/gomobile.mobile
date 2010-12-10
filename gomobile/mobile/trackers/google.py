"""

    Google Analytics tracking backends.

    Both Javascript based and image based.

"""

try:
    # Python >= 2.5
    from hashlib import md5
except ImportError:
    # Python < 2.5
    from md5 import md5

import zope.interface

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileTracker

import ga

class GoogleAnalyticsMobileTracker(object):
    """ Google Analytics mobile analytics tracker abstraction.

    Uses __utm.gif synchronous server calling for the visitor tracking.
    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId, debug):

        # Perform remote HTTP request to update GA stats
        url = ga.track_page_view(self.request, self.request.response, self.request.environ, trackingId, debug=debug, synchronous=False)

        # return '<!-- GA --> <img alt="" src="%s" />' % url # Tracker marker, does really nothing

        if url:
            return '<img class="google-analytics" alt="" src="%s" />' % url # Tracker marker, does really nothing
        else:
            return '<img class="google-analytics google-analytics-broken" alt="" src="" />'



class GoogleAnalyticsWebTracker(object):
    """ Allow using urchin Javascript tracking on mobile sites.

    Very easy to set-up, but does not support
    mobile browsers without Javascript.

    GA mobile does not officially support Python,
    so it might be pain sometimes to get it working, especially
    because GA does not have any means for developer debugging:
    __utm.gif gives you always HTTP 200 OK no matter what you toss in as
    the paramters. Site visitor count, however, is not updated.
    Using GA Javascript tracker we can guarantee the tracking works,
    at least on some phones.
    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId, debug):
        """
        """
        # Perform remote HTTP request to update GA stats

        return URCHIN_CODE % trackingId

# Async. Urchin tracking code
URCHIN_CODE="""
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', '%s']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>"""
