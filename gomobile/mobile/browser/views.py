__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import urllib

from zope.app.component.hooks import getSite
import zope.interface

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility
from zope.app.container.interfaces import INameChooser
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import aq_base, aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.browser import ploneview
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, queryUtility
from zope.app.component.hooks import getSite


from gomobile.mobile.interfaces import IMobileUtility, IMobileRequestDiscriminator, IMobileSiteLocationManager, MobileRequestType
       

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
    
class MobileTool(BrowserView):
    """ A context-aware wrapper for mobile site utilities.
    
    Provide convience functions for page templates.
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.discriminator = getUtility(IMobileRequestDiscriminator)
        self.location_manager = getUtility(IMobileSiteLocationManager)
                
        self.request_flags = self.discriminator.discriminate(self.context, self.request)
                
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
        return self.location_manager.rewriteURL(self.request, self.context.absolute_url(), MobileRequestType.MOBILE)
    
    def getMobilePreviewURL(self):
        """ Return URL used in phone simualtor.            
        """
        return self.location_manager.rewriteURL(self.request, self.context.absolute_url(), MobileRequestType.PREVIEW)
        
    def getWebSiteURL(self):
        """ Return the web version URL of this of context """        
        return self.location_manager.rewriteURL(self.request, self.context.absolute_url(), MobileRequestType.WEB)
    
    

