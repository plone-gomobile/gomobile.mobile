"""


    Old-fashioned uninstall script.
    
"""

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.setuphandlers import clean_up_content_annotations

def uninstall(portal, reinstall=False):

    if not reinstall:

        # normal uninstall
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.runAllImportStepsFromProfile('profile-gomobile.mobile:uninstall')
      
        clean_up_content_annotations(portal, ["mobile"])

        return "Ran all uninstall steps."
