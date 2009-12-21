"""

    Utility facilities to deal with mobile HTTP requests.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>"
__author_url__ = "http://www.twinapex.com"

import urlparse

import zope.interface
from zope import schema
from zope.component import getUtility, queryUtility
from zope.annotation import IAnnotations

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


class IVolatileContext(zope.interface.Interface):
    """ """

    context = schema.Object(zope.interface.Interface, description=u"Run-time reference accessor to the parent object this object belongs to")

    factory = schema.Object(zope.interface.Interface, description=u"Reference to the factory which created this run-time instance")

    def save():
        """ Write object to the database and construct connection with the parent object.
        """
from persistent import Persistent
class VolatileContext(Persistent):
    """ Mix-in class to provide non-persistent context  to persistent classes.

    Some subsystems (e.g. z3c.forms) expect objects to have a context reference to parent/site/whatever.
    However, storing this back-reference persistenly is not needed, as the factory
    method will always know the context.

    This helper class creates a context property which is volatile (never persistent),
    but can be still set on the object after creation or after database load.
    """

    zope.interface.implements(IVolatileContext)

    @property
    def context(self):
        return self._v_context

    @property
    def factory(self):
        return self._v_factory

    # http://docs.python.org/library/functions.htm
    def save(self):
        """ """
        self.factory.makePersistent(self)

class AnnotationPersistentFactory(object):
    """ A factory pattern to manufacture persistent objects stored within the parent object annotations.

    Until the first write, the default (non-persistent) object is return. This prevents
    possible situations where database read could cause write.

    The first write must call AnnotationPersistentFactory.makePersistent(object).
    Alternative, you can call AnnotationPersistentFactory.makePersistent(object)
    when entering the editing interface for the first time.

    After the first write, the saved persistent object is return.
    """


    def __init__(self, persistent_class, key):
        """
        @param persistent_class: Class reference / factory method which will create new objects.
            Created classes must conform VolatileContext interface

        @param key: ASCII string, Key name used with IAnnotations
        """
        self.persistent_class = persistent_class
        self.key = key
        self._assertProperlySetUp()

    def _assertProperlySetUp(self):
        """
        Check that the framework is properly set up
        """
        assert callable(self.persistent_class), "Factory is missing"

        assert hasattr(self.persistent_class, "context"), "The persistent object must support volatile context interface"

        assert self.key is not None, "You must give the annotations key"

    def makePersistent(self, object):
        """ Write created persistent object to the database.

        This will store the object on the annotations of its context.
        """
        assert isinstance(object, self.persistent_class), "Object %s was not type of %s" % (str(object), str(self.persistent_class))
        annotations = IAnnotations(object.context)
        annotations[self.key] = object

    def __call__(self, context):
        """ Called by Zope framework when doing a factory call.

        Usually this class is refered as <adapter factory=""> and
        this method creates a new, read-only, persistent object.
        """

        annotations = IAnnotations(context)

        if not self.key in annotations:
            # Construct a new (default) instance
            object = self.persistent_class()
        else:
            # Return the object stored previously
            object = annotations[self.key]

        # Set volatile context reference
        object._v_context = context
        object._v_factory = self

        return object


