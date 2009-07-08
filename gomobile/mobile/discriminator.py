"""

    Code for determining whether requests are mobile or web.

"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import zope.interface

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType

from zope.app.component.hooks import getSite

class DefaultMobileRequestDiscriminator(object):
    """ Determine which are web, mobile, mobile preview and mobile content admin HTTP requests.
    
    1. Determine preview and mobile requests based on a domain name.
       (m.xxx, xxx.mobi, mobi.xxx, mobile.xxx are considered to be mobile).
    
    2. Use HTTP GET query parameter view_mode to override the default behavior
       (for dummy testing)
       
    """
    
    zope.interface.implements(IMobileRequestDiscriminator)
    
    def __init__(self):
        pass
        
    
    def isMobileRequest(self, site, request, mobileDomainPrefixes):
        """ Determine should this request be rendered in mobile mode. """        

        #
        # Special HTTP GET parameter tellign
        # that render this as a preview request
        #            
        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True


        #
        # Determine if this is targeted to mobile domain
        # based on request domain name
        #
        if "HTTP_HOST" in request.environ:
            
            host = request.environ["HTTP_HOST"]
            
                    
            for prefix in mobileDomainPrefixes:
                if host.startswith(prefix + "."):
                    return True

                                    
        return False
    
    def isPreviewRequest(self, site, request, prefixes):
        """ Determine should this request be rendered in mobile mode. 
        
        
        """        

        #
        # If we are using preview. domain name
        # this is a preview request
        #
        
        if "HTTP_HOST" in request.environ:
            for prefix in prefixes:
                if request.environ["HTTP_HOST"].startswith(prefix):
                    return True

        #
        # Special HTTP GET parameter tellign
        # that render this as a preview request
        #
        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True
                
        return False    

    def isAdminRequest(self, site, request):    
        """ By default, assume all logged in users are admins.
        """ 
        return not site.portal_membership.isAnonymousUser()
    
    def discriminate(self, context, request):
        
        flags = []
                
        # Load settings from database
        try:
            properties = context.portal_properties.mobile_properties
            
            # It is possible to have several mobile domain prefixes,
            # but in the default config there is just one
            mobileDomainPrefixes = properties.mobile_domain_prefixes      
            previewDomainPrefixes = properties.preview_domain_prefixes
            
        except AttributeError:
            # Traversing happens when our product is not properly set up
            # or during the site launch. The loading order prevents 
            # us to access mobile_properties here, so it is 
            # safe to assume this was not a mobile request
            
            # (Because monkey-patch intercepts admin interface requests also
            # we need to make sure no exceptio gets through)
            flags.append(MobileRequestType.WEB)
            return flags
        

        # 1. Test against preview subdomains
        if self.isPreviewRequest(context, request, previewDomainPrefixes):
            flags.append(MobileRequestType.PREVIEW)
            flags.append(MobileRequestType.MOBILE)
        # 2. Test against mobile subdomains
        elif self.isMobileRequest(context, request, mobileDomainPrefixes):
            flags.append(MobileRequestType.MOBILE)    
        # 3. otherwise assume web request
        else:
            flags.append(MobileRequestType.WEB)

            # 4. show mobile management portlets based on 
            # if the user has logged in
            if self.isAdminRequest(context, request):
                flags.append(MobileRequestType.ADMIN)
        
            
        return flags
