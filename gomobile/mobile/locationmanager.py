__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

import urlparse

import zope.interface

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType, IMobileSiteLocationManager
from zope.app.component.hooks import getSite

class DomainNameBasedMobileSiteLocationManager(object):
    """ Present the content differently based on its domain name.
    
    xxx.com -> web site
    mobi.xxx.com -> mobile site
    preview.xxx.com -> mobile site preview
    
    There transforms here are port neutral i.e.
    the port of the orignal HTTP request is preserved in the URL.
    
    Use portal_properties.mobile_properties domains names 
    to change the content media. URI part stays same for all content.    
    """
    
    zope.interface.implements(IMobileSiteLocationManager)
                    
    def _getBaseDomainName(self, domain, properties):
        """        
        @param domain: domain name as string
        @param properties: Mobile site config (see propertiestool.xml)
        @return: domain name without mobile or preview prefixes
        """
        parts = domain.split(".")
        
        all_subdomain_prefixes = properties.mobile_domain_prefixes + \
                                 properties.preview_domain_prefixes +  \
                                 properties.web_domain_prefixes        
        
        # Chop prefix subdomain
        for p in all_subdomain_prefixes:
            if parts[0] == p:
                parts = parts[1:]
                break
            
        return ".".join(parts)
    
    def _prefixDomain(self, domain, mode, properties):
        """ Add subdomain discriminator to domain host name
        
        xxx.com -> m.xxx.com
        
        @param mode: MobileRequestType
        @param domain: domain name as string
        @param properties: Mobile site config (see propertiestool.xml)
        @return: mangled domain name
        
        """
        if mode == MobileRequestType.MOBILE:
            # Use first prefix on the list when rewriting
            return properties.mobile_domain_prefixes[0] + "." + domain
        elif mode == MobileRequestType.PREVIEW:
            # Use first prefix on the list when rewriting
            return properties.preview_domain_prefixes[0] + "." + domain
        else:
            # Assume web domains shouldn't get prefixed
            return domain
            
    def _replaceNetworkLocation(self, url, mode, properties):
        """ Rewrite domain name in the site URL.
        
        @param url: url to be rewritten
        @param mode: One of MobileRequestType pseudo constants
        @param properties: Mobile site config (see propertiestool.xml)
        """
        parts = urlparse.urlparse(url)
        parts = list(parts)
        
        # domain name + port as tuple
        domainAndPort = parts[1].split(":")
        
        base = self._getBaseDomainName(domainAndPort[0], properties)
        prefixed =  self._prefixDomain(base, mode, properties)
        
        domainAndPort[0] = prefixed
                
        parts[1] = ":".join(domainAndPort)
        
        return urlparse.urlunparse(parts)
    
    def rewriteURL(self, request, url, mode):
        
        # Load PloneSite object from thread locals
        site = getSite()
        
        # Load config from the database
        properties = site.portal_properties.mobile_properties
        
        return self._replaceNetworkLocation(url, mode, properties)
    
    
    def intercept(self, site, request):
        pass
        
            
