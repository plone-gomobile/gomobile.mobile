"""

    Helper middleware for Plone mobile edition.
    
    TODO: UNDONE

    
"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

from paste.request import get_cookies, parse_headers

class SubdomainCookieSharingMiddleware:
    """ WSGI compliant middleware for setting cookie domain info.
    
    By default, Plone cookies are not shared with subdomains.
    Since mobile site and preview page rendering use subdomains,
    hitting a preview page requires reauth.
    
    This middleware works around the problem by setting the domain header
    of the cookie.
    """
    def __init__(self, app=None):
        self.app = app
            
    def __call__(self, environ, start_response):
        # TODO: WAS BAD IDEA
        pass
   

def subdomain_middleware_factory(app, global_conf, **local_conf):
    """ Paste Deploy script compliant middleware constructor.
    
    http://pythonpaste.org/deploy/#paste-filter-factory
    """
    return SubdomainCookieSharingMiddleware(app)


                
