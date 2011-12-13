__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import logging
import re
import urlparse

import zope.interface
from zope.app.component.hooks import getSite

from gomobile.mobile.interfaces import MobileRequestType
from gomobile.mobile.interfaces import IMobileSiteLocationManager

logger = logging.getLogger("Plone")
# Roughly match ip address.  Taken from
# http://www.regular-expressions.info/examples.html
IP_ADDRESS_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


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

    def __init__(self, context, request):
        """
        """
        self.context = context
        self.request = request

        self.properties = self.getProperties()

    def getProperties(self):
        """ Error-tolerant mobile_properties getter.

        Work correctly under special traversing circumstances
        (e.g. ZMI in Zope App root).
        """

        # Load PloneSite object from thread locals
        site = getSite()
        if site == None:
            logger.debug("No site was available in "
                        "locationmanager.rewriteURL()")
            return None

        # Load config from the database
        if hasattr(site.portal_properties, "mobile_properties"):
            return site.portal_properties.mobile_properties
        # We implicitly return None here
        logger.debug("No mobile_properties found.")

    def getBaseDomainName(self, domain):
        """ Get the domain name with all unnecessary prefixes and
        suffixes stripped out.

        We use the listing in mobile properties to filter out prefixes.

        Example::
            m.mfabrik.com -> mfabrik.com


        @param domain: domain name as string

        @return: domain name without mobile or preview prefixes
        """

        properties = self.properties
        if self.properties is None:
            return domain
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

    def prefixDomain(self, domain, mode):
        """ Add subdomain discriminator to domain host name

        xxx.com -> m.xxx.com

        @param mode: MobileRequestType
        @param domain: domain name as string

        @return: mangled domain name

        """

        properties = self.properties
        if self.properties is None:
            return domain
        if IP_ADDRESS_PATTERN.match(domain):
            # m.127.0.0.1 makes no sense
            return domain
        if mode == MobileRequestType.MOBILE:
            # Use first prefix on the list when rewriting
            if properties.mobile_domain_prefixes:
                return properties.mobile_domain_prefixes[0] + "." + domain
            else:
                logger.warn('No mobile_domain_prefixes found.')
        elif mode == MobileRequestType.PREVIEW:
            # Use first prefix on the list when rewriting
            if properties.preview_domain_prefixes:
                return properties.preview_domain_prefixes[0] + "." + domain
            else:
                logger.warn('No preview_domain_prefixes found.')
        # Assume web domains shouldn't get prefixed.
        # Also, we end up here when we could not find a domain prefix above.
        return domain

    def rewriteDomain(self, domain, mode):
        """ Changes domain name to point to web/mobile server.

        @param domain: Domain name as a string, without port like 8080
          and without www/mobile prefixes like m.

        @param mode: One of "mobile", "web" etc. MobileRequestType constants

        @return: Domain name for redirect request as a string
        """
        return self.prefixDomain(domain, mode)

    def replaceNetworkLocation(self, url, mode):
        """ Rewrite domain name in the site URL.

        @param url: url to be rewritten
        @param mode: One of MobileRequestType pseudo constants
        """

        parts = urlparse.urlparse(url)
        parts = list(parts)

        # domain name + port as tuple
        domainAndPort = parts[1].split(":")

        base = self.getBaseDomainName(domainAndPort[0])
        prefixed = self.rewriteDomain(base, mode)

        domainAndPort[0] = prefixed

        parts[1] = ":".join(domainAndPort)

        return urlparse.urlunparse(parts)

    def rewriteURL(self, url, mode):

        if self.properties is None:
            #logger.warn("Cannot rewrite URL - no mobile_properties "
            #            "available - " + url)
            # Don't do anything exceptional here as we might be called
            # in pre traverse hook or other unsafe location
            return url

        return self.replaceNetworkLocation(url, mode)
