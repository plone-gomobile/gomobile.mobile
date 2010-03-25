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
    """ Google Analytics mobile analytics tracker abstraction. 
    
    Note: Currently tracking is done synchronously
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
            return ""

