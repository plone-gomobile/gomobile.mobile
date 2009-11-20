"""

    Utility facilities to deal with mobile HTTP requests.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__author_url__ = "http://www.twinapex.com"

import urlparse

import zope.interface
from zope.component import getUtility, queryUtility

from mobile.sniffer.utilities import get_user_agent
from mobile.heurestics.simple import is_low_end_phone

from Products.Five.browser import BrowserView
from gomobile.mobile.interfaces import IMobileUtility

class MobileUtility(object):
    """ Zope 3 utility for mobile actions. """

    zope.interface.implements(IMobileUtility)

    def isMobileRequest(self, request):
        """ Determine should this request be rendered in mobile mode. """

        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        if "HTTP_HOST" in request.environ:
            # Unit tests don't have HTTP_HOST
            if "mobi." in request.environ["HTTP_HOST"]:
                return True

        if self.isPreviewRequest(request):
            return True

        return False

    def isPreviewRequest(self, request):
        """ Determine should this request be rendered in mobile mode. """

        if "HTTP_HOST" in request.environ:
            if "preview." in request.environ["HTTP_HOST"]:
                return True

        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        return False

    def isLowEndPhone(self, request):
        """ @return True: If the user is visiting the site using a crappy mobile phone browser.

        Low end phones have problem with:

            - Complex HTML syntax

            - Several images on the same page

            - Advanced CSS styles

        Before using the techniques above please filter them away for the crappy phones.
        This concerns at least Nokia Series 40 phones.

        Note that Opera Mini browser works smoothly on low end phones too...
        """
        return is_low_end_phone(request)


def getCachedMobileProperties(context, request):
    """ Cached access to mobile properties of the site.

    Will look up mobile properties from the database or return the cached instance.
    """
    return context.portal_properties.mobile_properties


def debug_layers(context):
    from zope.component import adapts
    from zope.component import getSiteManager
    from zope.component import queryMultiAdapter
    from zope.component import getSiteManager
    from zope.component import getAllUtilitiesRegisteredFor

    from plone.browserlayer.interfaces import ILocalBrowserLayerType
    from plone.browserlayer.utils import register_layer, unregister_layer
    return
    active = context.REQUEST.__provides__.__iro__
    print active



class VolatileContext(object):
    """ Mix-in class to provide context variable to persistent classes which is not persitent.

    Some subsystems (e.g. forms) expect objects to have a reference to parent/site/whatever.
    However, it might not be a wise idea to have circular persistent references.

    This helper class creates a context property which is volatile (never persistent),
    but can be still set on the object after creation or after database load.
    """

    # _v_ attribute prefix marks volatile ZODB references
    _v_context = None


    def _set_context(self, context):
        self._v_context = context

    def _get_context(self):
        return self._v_context

    context = property(_get_context, _set_context)