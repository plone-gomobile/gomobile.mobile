__license__ = "GPL 2"
__copyright__ = "2009-2011 mFabrik Research Oy"

import random
from StringIO import StringIO

from Products.GenericSetup import profile_registry, EXTENSION
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

from plone.browserlayer.utils import unregister_layer

def fix_browserlayer(site):
    """
    This was not properly done before 1.0 using theme layers. There might be corrupted registry on old sites. 
    """
    try:
        unregister_layer("gomobile.mobile")
    except KeyError:
        pass

def importFinalSteps(context):
    """
    The last bit of code that runs as part of this setup profile.
    """

    # We check from our GenericSetup context whether we are running
    # add-on installation for your product or any other proudct
    if context.readDataFile('gomobile.install.various.txt') is None:
        # Not your add-on
        return
 
    site = context.getSite()
    
    # Reseed mobile image resizer secret
    site.portal_properties.mobile_properties.image_resizer_secret = str(random.randint(0, 999999999))

    fix_browserlayer(site)

    
def removeImportSteps(context):

    # http://plone.org/documentation/kb/genericsetup-uninstalling-import-steps
    setup = getToolByName(self, 'portal_setup')
    
    setup.setImportContext('profile-myproduct:default')
    
    ir = setup.getImportStepRegistry()
    
    #print ir.listSteps()  # for debugging and seeing what steps are available
    
    # delete the offending step
    try:
        del ir._registered['myproduct-badstep']
    except KeyError:
        pass
    
    # commit the changes to the zodb
    import transaction
    txn = transaction.get()
    txn.commit()
    
def uninstall(context):
    """
    The last bit of code that runs as part of this setup profile.
    """

from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.interfaces import IFolderish


def clean_up_content_annotations(portal, names):
    """
    Remove objects from content annotations in Plone site,

    This is mostly to remove objects which might make the site un-exportable 
    when eggs / Python code has been removed.

    @param portal: Plone site object
    
    @param names: Names of the annotation entries to remove
    """
    
    output = StringIO()
    
    def recurse(context):
        """ Recurse through all content on Plone site """
                
        try:
            annotations = IAnnotations(context)
        except TypeError:
            # Some special objects, like AT criterion on Plone 4, might not support annotations
            print  >> output, "Annotations where not available on item:" + str(context)
            return
        
        #print  >> output, "Recusring to item:" + str(context)
        # print annotations
        
        for name in names:
            if name in annotations:
                print >> output, "Cleaning up annotation %s on item %s" % (name, context.absolute_url()) 
                del annotations[name]
        
        # Make sure that we recurse to real folders only,
        # otherwise contentItems() might be acquired from higher level
        if IFolderish.providedBy(context):
            for id, item in context.contentItems():
                recurse(item)
        
    recurse(portal)
    
    return output
    
