"""

    AdMob tracker - register at www.admob.com


    The orignal code courtesy of http://www.djangosnippets.org/snippets/883/

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

class GoogleAnalyticsTracker(object):
    """

    For tracking id, use your AdMob site id.

    Note: If ads are enabled on your AdMob acount will display ads and is not invisible.

    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId):
        
        # Perform remote HTTP request to update GA stats
        ga.track_page_view(self.request, self.request.response, self.request.environ, trackingId)

        return "<!-- GA -->" # Tracker marker, does really nothing

