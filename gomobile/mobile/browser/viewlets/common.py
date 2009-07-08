__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter

class ConvergedViewletMixin(object):
    """ Viewlet which is aware whether it is in web or mobile
        and does not render itself in the wrong environment.
        
    """
    def getTool(self):
        return self.context.unrestrictedTraverse("mobile_tool")

    def isOnCorrectMedia(self):
        raise NotImplementedError("Subclass must implement")
    
    def render(self):
        """ Conditionally render the portlet only if we are on a correct media. """
        if self.isOnCorrectMedia():
            return ViewletBase.render(self)
        else:
            return ""
    
    def getCanvasScaledImage(self, *args, **kwargs):
        """ Return image src which will go through image resizer to make image fit to the mobile screen.
        
        """        

        resizer = self.context.restrictedTraverse("@@mobile_image_resizer")
        return resizer.getResizedImageURL(*args, **kwargs)
    
    def getCanvaScaledBackgroundImage(self, *args, **kwargs):
        """ Return style attribute to scale background image """
        src = self.getCanvasScaledImage(*args, **kwargs)
        return "background-image: url(" + src + ")"

       
class WebOnlyViewletMixin(ConvergedViewletMixin):
    """ Viewlet which is in a shared mobile/web viewlet manager, but should be rendered in web only. """

    def isOnCorrectMedia(self):
        return not self.getTool().isMobileRequest()

class MobileOnlyViewletMixin(ConvergedViewletMixin):
    """ Viewlet which is in a shared mobile/web viewlet manager, but should be rendered in mobile only. """
    
    def isOnCorrectMedia(self):
        return self.getTool().isMobileRequest()
    


class MobileFolderListingViewlet(MobileOnlyViewletMixin, ViewletBase):
    """ Displays the contents of the current folder. 
    
    We don't have navigation here, so we need to emulate it.
    
    TODO: This class must be scrapped and rewritten.
    """
    
    index = ViewPageTemplateFile('mobile_folder_listing.pt')
    
    
    def getLanguage(self):
        """ LinguaPlone compatible language getter """
        
        if not "LANGUAGE" in self.request.other:
            # We are called in before traverse hook
            # LanguageTool language bindings have not been run yet...
            # run it
            self.context.portal_languages.getLanguageBindings()
        
        lang = self.request.other["LANGUAGE"]
        
        return lang
    

    def update(self):
        """ TODO: rewrite using enhanced navtree functions now when we have them """
        
        self.items = []
                
        
        if not self.isOnCorrectMedia():
            # Do not to heavy calculations for web view
           return
            
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        context = aq_inner(self.context)
        
        
        from Products.CMFCore.interfaces._content import IFolderish
        if not IFolderish.providedBy(context):
            # Default page - use folder above
            bads = [context]
            context = context.aq_parent
        else:
            bads = []
                                
        bad_types = context.portal_properties.navtree_properties.metaTypesNotToList
        bad_types = list(bad_types)
        #bad_types.append("Image")
        #bad_types.append("ATImage")
        
        # Test if this item can control its listing
        # TODO:Use interfaces here
        if hasattr(context, "Schema"):    
            schema = context.Schema()
            if "mobileFolderListing" in schema:
                field = schema["mobileFolderListing"]
                value = field.get(context)
                
                # Listing prohibited
                if value != True:
                    self.items = []
                    return
        
        if hasattr(context, "default_page"):    
            default_page = context.default_page
        else:
            default_page = None
        
        def is_excluded(subobject):
        
            if subobject == default_page:
                return True
                                
            if hasattr(subobject, "getExcludeFromNav"):
                return subobject.getExcludeFromNav()
            return False

        items = context.listFolderContents()
        items = [ i for i in items if not i in bads ]        
        items = [ i for i in items if not i.meta_type in bad_types ]
        items = [ i for i in items if not is_excluded(i) ]
        
        # Filter by language
        language = self.getLanguage()
        if language:
            
            def item_lang(x):
                if hasattr(x, "getLanguage"):
                    return i.getLanguage()
                else:
                    return None
            
            items = [ i for i in items if item_lang(i) == language ]
        
        # TODO: Fix this depedecncy somehow!
        # Check listed o
        #from gomobile.convergence.tools import checkMediaFilter, filterObject
        #from gomobile.convergence.interfaces import ContentMediaOption
        #strategy = ContentMediaOption.MOBILE
            
        #items = [ i for i in items if filterObject(obj, strategy) ]

        # Now check which items have navigation button images
        self.items = []
        for item in items:
            image = None

            # gomobile.convergence extender hooks in here
            field = item.Schema().getField("mobileButtonImage")
            if field:
                value = field.get(item)
                if value:
                    image = item.absolute_url() + "/mobileButtonImage"
                
            self.items.append({ "item" : item, "image": image})
            
                        
from plone.app.layout.viewlets import common
class LogoViewlet(MobileOnlyViewletMixin, common.LogoViewlet):    
    """ Mobile site logo """
    index = ViewPageTemplateFile('logo.pt')
    
    def update(self):
        common.LogoViewlet.update(self)
        self.portal = self.portal_state.portal()        
        logoName = "logo.jpg"        

class FooterViewlet(MobileOnlyViewletMixin, common.ViewletBase):    
    """ Mobile site footer """
    index = ViewPageTemplateFile('footer.pt')

    def update(self):
        """ Make sure that we have all view template context variables set up """
        
        common.ViewletBase.update(self)

        # Get tabs (top level navigation links)
        context_state = getMultiAdapter((self.context, self.request),
                                    name=u'plone_context_state')
        actions = context_state.actions()

        
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                       name='portal_tabs_view')
    
        
        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)

    
class PathBarViewlet(MobileOnlyViewletMixin, common.PathBarViewlet):    
    """ Mobile site breadcrumbs """
    index = ViewPageTemplateFile('path_bar.pt')
    
           
from plone.app.layout.analytics.view import AnalyticsViewlet
class MobileAwareAnalyticsViewlet(WebOnlyViewletMixin, AnalyticsViewlet):
    """ Do not render Google Analytics in mobile """

    def render(self):
        """ Conditionally render the portlet only if we are on a correct media. """
        if self.isOnCorrectMedia():
            return AnalyticsViewlet.render(self)
        else:
            return ""
    
