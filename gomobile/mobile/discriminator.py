"""

    Code for determining whether requests are mobile or web HTTP requests and how user interface should be rendered.

    Go Mobile for Plone project home page: http://webandmobile.mfabrik.com

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"

import logging
import zope.interface

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType, IUserAgentSniffer
from gomobile.mobile.utilities import get_host, is_numeric_ipv4

from zope.app.component.hooks import getSite

logger = logging.getLogger("gomobile.discriminator")

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


    def isMobileRequest(self, site, request, mobileDomainPrefixes, mobileDomainSuffixes, mobileViaIP):
        """ Determine should this request be rendered in mobile mode.

        @return: True or False
        """

        #
        # Special HTTP GET query parameter telling
        # that render this as a preview request
        #
        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        #
        # Determine if this is targeted to mobile domain
        # based on request domain name
        #
        host = get_host(request)


        if host:

            host = host.lower()

            # print "Got host:" + str(host)

            host = host.split(":")[0] # Remove port

            # Special rule to use mobiles for LAN/WLAN traffic
            if mobileViaIP and is_numeric_ipv4(host):
                return True


            # Go through each subdomain name and compare it to mobile markers
            for part in host.split(".")[0:-1]:
                for prefix in mobileDomainPrefixes:
                    #print "Comparing " + prefix + " " + part
                    if part == prefix:
                        return True

            for suffix in mobileDomainSuffixes:
                if host.endswith("." + suffix):
                    return True

        return False

    def isPreviewRequest(self, site, request, prefixes):
        """ Determine should this request be rendered in mobile mode.

        @return: True or False
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
        # Special HTTP GET parameter telling
        # that render this as a preview request
        #
        if request.get("view_mode") == "mobile":
            # IFRAME request
            return True

        return False

    def isAdminRequest(self, site, request):
        """ By default, assume all logged in users are admins.
        """

        try:
            portal_membership = getToolByName(site, 'portal_membership')
        except AttributeError:
            # Can't access member properties
            return False

        return not portal_membership.isAnonymousUser()

    def discriminate(self, context, request):

        flags = []

        # Load settings from database
        try:

            portal_properties = getToolByName(context, "portal_properties")

            properties = portal_properties.mobile_properties

            # It is possible to have several mobile domain prefixes,
            # but in the default config there is just one
            mobileDomainPrefixes = properties.mobile_domain_prefixes
            mobileDomainSuffixes = properties.mobile_domain_suffixes
            previewDomainPrefixes = properties.preview_domain_prefixes

            # Migration compatible
            mobileViaIP = getattr(properties, "serve_mobile_via_ip", False)

        except AttributeError:

            # Traversing happens when our product is not properly set up
            # or during the site launch. The loading order prevents
            # us to access mobile_properties here, so it is
            # safe to assume this was not a mobile request

            # UTF-8 issues my ensure
            try:
                context_desc = str(context)
            except:
                context_desc= ""

            logger.debug("Cannot access mobile properties, having context:" + context_desc)

            # (Because monkey-patch intercepts admin interface requests also
            # we need to make sure no exceptio gets through)
            flags.append(MobileRequestType.WEB)
            return flags


        # 1. Test against preview subdomains
        if self.isPreviewRequest(context, request, previewDomainPrefixes):
            flags.append(MobileRequestType.PREVIEW)
            flags.append(MobileRequestType.MOBILE)
        # 2. Test against mobile subdomains
        elif self.isMobileRequest(context, request, mobileDomainPrefixes, mobileDomainSuffixes, mobileViaIP):
            flags.append(MobileRequestType.MOBILE)
        # 3. otherwise assume web request
        else:
            flags.append(MobileRequestType.WEB)

            # 4. show mobile management portlets based on
            # if the user has logged in
            if self.isAdminRequest(context, request):
                flags.append(MobileRequestType.ADMIN)


        return flags
