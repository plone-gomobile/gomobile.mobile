"""
    Suppoer behavior assignments for non-dexerity objects.

    Define default mechanism to determine whether thr header animation
    is enabled (the header is editable) on content.

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

import zope.interface
import zope.component
from plone.behavior.interfaces import IBehavior, IBehaviorAssignable
from Products.CMFCore.interfaces import IContentish

from interfaces import IMobileContentish

class BehaviorAssignable(object):
    """ Dummy policy which allows you to place headers on every content object.

    TODO: This probably conflicts with everything else, but plone.behavior didn't provide
    documentation how assignables and Plone are related.
    """
    zope.interface.implements(IBehaviorAssignable)
    zope.component.adapts(IMobileContentish)

    def __init__(self, context):
        self.context = context

    def supports(self, behavior_interface):
        return True

zope.component.provideAdapter(BehaviorAssignable)
