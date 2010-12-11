"""

    Mobile options edit form.

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>"
__docformat__ = "epytext"

from Acquisition import aq_inner
import zope.interface
from zope import schema
from zope.component import getUtility, queryUtility
from zope.component import getMultiAdapter, queryMultiAdapter
from Products.Five.browser import BrowserView

import z3c.form.form
from z3c.form import subform
from z3c.form import field
from z3c.form import group

from gomobile.convergence.interfaces import IOverrideForm, IOverrider
from plone.z3cform.layout import FormWrapper, wrap_form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile

from gomobile.mobile.behaviors import IMobileBehavior

class MobileForm(z3c.form.form.EditForm):
    """ Folder/page specific mobile publishing options """

    fields = field.Fields(IMobileBehavior)

    prefix = "mobile"
    
    label = u"Mobile navigation settings"

    def update(self):
        return z3c.form.form.EditForm.update(self)

    def getContent(self):
        behavior = IMobileBehavior(self.context)
        return behavior

    def applyChanges(self, data):
        # Call super
        content = self.getContent()
        val = z3c.form.form.EditForm.applyChanges(self, data)

        # Write behavior to database
        content = self.getContent()
        content.save()

        self.status = u"Mobile navigation settings changed"
        
        return val

MobileFormView = wrap_form(MobileForm)
