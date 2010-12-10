__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import urlparse

import zope.interface

from Products.Five.browser import BrowserView

from zope.component import getUtility, queryUtility

from gomobile.mobile.interfaces import IMobileUtility

# TODO: This module is being phased out
