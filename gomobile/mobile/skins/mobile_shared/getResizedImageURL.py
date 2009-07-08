__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

## Controller Python Script ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=path
##title=Initial post-login actions
##

portal_url = context.portal_url()
view = context.restrictedTraverse("@@mobile_image_resizer")
uri = view.getResizedImageURL(path)
return uri
