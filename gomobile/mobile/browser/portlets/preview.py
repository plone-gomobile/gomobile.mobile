__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

from zope.interface import implements
from zope.component import getUtility
from zope import schema

from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlets.interfaces import IPortletDataProvider

from zope.component import getUtility, queryUtility
from gomobile.mobile.interfaces import IMobileUtility
from gomobile.mobile import GMMobileMF as _

class IPreviewPortlet(IPortletDataProvider):
    """ Define buttons for mobile preview """
    pass

class Renderer(base.Renderer):
    """ Overrides static.pt in the rendering of the portlet. """

    index = ViewPageTemplateFile('preview.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.site_url = getToolByName(context, 'portal_url')

    def getMobileSiteURL(self):
        """ """
        mobile_tool = self.context.unrestrictedTraverse("mobile_tool")
        return mobile_tool.getMobileSiteURL()

    def getMobilePreviewURL(self):
        """ """
        mobile_tool = self.context.unrestrictedTraverse("mobile_tool")
        return mobile_tool.getMobilePreviewURL()

    def is_visible(self):
      membership_tool=self.context.portal_membership
      return not membership_tool.isAnonymousUser()

    def render(self):
        if self.is_visible():
          return self.index()
        else:
          return ""

class Assignment(base.Assignment):
    """ Assigner for grey static portlet. """
    implements(IPreviewPortlet)

    title = _(u"Mobile preview")

class AddForm(base.NullAddForm):
    """ Make sure that add form creates instances of our custom portlet instead of the base class portlet. """
    def create(self):
        return Assignment()
