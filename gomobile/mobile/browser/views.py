"""

    Various mobile HTTP request handlers and context depending utilities.

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"

import urllib

from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import getSecurityManager


import zope.interface
from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser
from zope.app.component.hooks import getSite
from zope.component import getUtility, queryUtility
from zope.app.component.hooks import getSite

from five import grok
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from OFS.SimpleItem import SimpleItem
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from Products.CMFPlone.browser import ploneview
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.interfaces._content import IFolderish
from AccessControl import getSecurityManager
from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, IMobileSiteLocationManager, MobileRequestType
from gomobile.mobile.interfaces import IMobileContentish
from gomobile.mobile.behaviors import IMobileBehavior

from mobile.heurestics.simple import format_phone_number_href, is_javascript_supported

grok.templatedir("templates")

class MobileSimulator(BrowserView):
    """ Render mobile site preview in phone simulator view.

    """

    context = None
    request = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.membership = context.portal_membership

    def __call__(self):
        pass


class MobileSimulatorIFrame(grok.View):
    """ Create <iframe> snippet needed to render the simulator page loader.
    """

    grok.context(IMobileContentish)

    def getMobilePreviewURL(self):
        """ """
        mobile_tool = self.context.unrestrictedTraverse("@@mobile_tool")
        return mobile_tool.getMobilePreviewURL()


class MobileTool(BrowserView):
    """ A context-aware wrapper for mobile site utilities.

    Provide convience functions for page templates to deal with mobile HTTP requests.
    This is exposed to page template as @@mobile_tool view and page templates
    can make conditional assumptions based on the provided tools and information.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.discriminator = getUtility(IMobileRequestDiscriminator)
        self.location_manager = getMultiAdapter((self.context, self.request), IMobileSiteLocationManager)
        self.request_flags = self.discriminator.discriminate(self.context, self.request)

    def getUtility(self):
        return getUtility(IMobileUtility)

    def isMobileRequest(self):
        return MobileRequestType.MOBILE in self.request_flags

    def isPreviewRequest(self):
        return MobileRequestType.PREVIEW in self.request_flags

    def isWebRequest(self):
        return MobileRequestType.WEB in self.request_flags

    def isAdminRequest(self):
        return MobileRequestType.ADMIN in self.request_flags

    def getMobileSiteURL(self):
        """ Return the mobile version of this context"""
        return self.location_manager.rewriteURL(self.context.absolute_url(), MobileRequestType.MOBILE)

    def getMobilePreviewURL(self):
        """ Return URL used in phone simualtor.
        """
        return self.location_manager.rewriteURL(self.context.absolute_url(), MobileRequestType.PREVIEW)

    def getWebSiteURL(self):
        """ Return the web version URL of this of context """
        return self.location_manager.rewriteURL(self.context.absolute_url(), MobileRequestType.WEB)

    def isLowEndPhone(self):
        """ @return True: If the user is visiting the site using a crappy mobile phone browser """
        return self.getUtility().isLowEndPhone(self.request)

    def shouldRunJavascript(self):
        """ @return True: If the user is visiting the site using a crappy mobile phone browser """
        return is_javascript_supported(self.request)


class FolderListingView(BrowserView):
    """ Mobile folder listing helper view

    Use getItems() to get list of mobile folder listable items for automatically generated
    mobile folder listings (touch button list).
    """

    def getListingContainer(self):
        """ Get the item for which we perform the listing
        """
        context = self.context.aq_inner
        if IFolderish.providedBy(context):
            return context
        else:
            return context.aq_parent

    def getActiveTemplate(self):
        state = getMultiAdapter((self.context, self.request), name=u'plone_context_state')
        return state.view_template_id()

    def getTemplateIdsNoListing(self):
        """
        @return: List of mobile-specific ids found from portal_properties where not to show folder listing
        """

        try:
            from gomobile.mobile.utilities import getCachedMobileProperties
            context = aq_inner(self.context)
            mobile_properties = getCachedMobileProperties(context, self.request)
        except:
            mobile_properties = None

        return getattr(mobile_properties, "no_folder_listing_view_ids", [])


    def filterItems(self, container, items):
        """ Apply mobile specific filtering rules

        @param items: List of context brains
        """

        # Filter out default content
        default_page_helper = getMultiAdapter((container, self.request), name='default_page')

        portal_state = getMultiAdapter((container, self.request), name='plone_portal_state')

        # Active language
        language = portal_state.language()

        # Return  the default page id or None if not set
        default_page = default_page_helper.getDefaultPage(container)

        security_manager = getSecurityManager()

        meta_types_not_to_list = container.portal_properties.navtree_properties.metaTypesNotToList

        current_content = self.context.aq_inner

        def show(item):
            """ Filter whether the user can view a mobile item.

            @param item: Real content object (not brain)

            @return: True if item should be visible in the listing
            """

            # Check from mobile behavior should we do the listing
            try:
                behavior = IMobileBehavior(item)
                appearInFolderListing = behavior.appearInFolderListing
            except TypeError:
                # Site root or some weird object, give up
                appearInFolderListing = True

            if not appearInFolderListing:
                # Default to appearing
                return False

            # Default page should not appear in the quick listing
            if item.getId() == default_page:
                return False

            if item.meta_type in meta_types_not_to_list:
                return False

            if item == current_content:
                # Do not show the currently viewed page itself in the folder listing
                return False

            # Two letter language code
            item_lang = item.Language()

            # Empty string makes language netral content
            if item_lang not in ["", None]:
                if item_lang != language:
                    return False

            # Note: getExcludeFromNav not necessarily exist on all content types
            if hasattr(item, "getExcludeFromNav"):
                if item.getExcludeFromNav():
                    return False

            # Does the user have a permission to view this object
            if not security_manager.checkPermission(permissions.View, item):
                return False

            return True

        return [ i for i in items if show(i) == True ]


    def constructListing(self):

        # Iterable of content items for the item listing
        items = []

        # Check from mobile behavior should we do the listing
        try:
            behavior = IMobileBehavior(self.context)
            do_listing = behavior.mobileFolderListing
        except TypeError:
            # Site root or some weird object, give up
            do_listing = False

        # Do listing by default, must be explictly disabledc
        if not do_listing:
            # No mobile behavior -> no mobile listing
            return None

        container = self.getListingContainer()

        # Do not list if already doing folder listing
        template = self.getActiveTemplate()
        #print "Active template id:" + template
        if template in self.getTemplateIdsNoListing():
            # Listing forbidden by mobile rules
            return None

        portal_properties = getToolByName(container, "portal_properties")
        navtree_properties = portal_properties.navtree_properties
        if container.meta_type in navtree_properties.parentMetaTypesNotToQuery:
            # Big folder... listing forbidden
            return None

        state = container.restrictedTraverse('@@plone_portal_state')

        #print "Performing mobile folder listing"
        items = container.listFolderContents()

        items = self.filterItems(container, items)

        return items

    def getItems(self):
        """
        @return: Items as a list.
        """
        items = self.constructListing()
        if items == None:
            return []
        return list(items)

class PhoneNumberFormatterView(BrowserView):
    """
    Helper view to format phone numbers so that they appear as dial-in links.

    Directly use underlying mobile.* package formatters.
    """


    def format(self, number):
        """
        """
        return format_phone_number_href(self.request, number)

