"""

    Mobile sitemap support.

    http://www.google.com/support/webmasters/bin/answer.py?hl=en&answer=34648

    http://mfabrik.com

"""

__license__ = "GPL 2"
__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__docformat__ = "epytext"


from gzip import GzipFile
from cStringIO import StringIO

from Products.Five import BrowserView
from zope.publisher.interfaces import NotFound
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.sitemap import sitemap as base
from plone.memoize import ram

def _render_cachekey(fun, self):
    # Cache by filename
    mtool = getToolByName(self.context, 'portal_membership')
    if not mtool.isAnonymousUser():
        raise ram.DontCache

    url_tool = getToolByName(self.context, 'portal_url')
    catalog = getToolByName(self.context, 'portal_catalog')
    counter = catalog.getCounter()
    return '%s/%s/%s' % (url_tool(), self.get_filename(), counter)

class LanguageAwareMobileSitemap(base.SiteMapView):
    """
    Allow generation of language specific sitemaps.

    Example Google Webmaster tools links:

    * http://yoursite/@@mobile_sitemap?language=fi&mode=mobile

    * http://yoursite/@@mobile_sitemap?language=fi&mode=mobile

    * http://yoursite/@@mobile_sitemap?language=ALL&mode=web

    Example test runs (does not GZip content):

    * http://yoursite/@@mobile_sitemap?language=fi&mode=mobile&test
    """

    template = ViewPageTemplateFile("templates/mobile-sitemap.pt")

    def getMode(self):
        """
        Should we pages as mobile.

        @return: "web" or "mobile"
        """
        mode = self.request.form.get("mode", "mobile")
        return mode

    def getLanguage(self):
        """
        Read language from the request.

        @return: Two letter language code or "ALL"
        """
        lang = self.request.form.get("language", None)

        # Enforce we do not leak wrong language items
        if lang == None:
            raise RuntimeError("Please give two letter language code or 'ALL' as 'language' GET parameter")

        # Some basic validation
        assert (len(lang)==2 or len(lang) == 3), "Bad input language"

        return lang

    def get_filename(self):
        """
        Calculate GZipped filename.
        """
        #print "Lang:" + str(self.getLanguage())
        #print "Mode:" + str(self.getMode())
        return self.getLanguage() + "-" + self.getMode() + "-sitemap.xml.gz"

    @ram.cache(_render_cachekey)
    def generate(self):
        """Generates the Gzipped sitemap."""
        xml = self.template()
        fp = StringIO()
        gzip = GzipFile(self.get_filename(), 'w', 9, fp)
        gzip.write(xml)
        gzip.close()
        data = fp.getvalue()
        fp.close()
        return data

    def uncompressed(self):
        """
        Return uncompressed data
        """
        return self.template()

    def objects(self):
        """Returns the data to create the sitemap."""
        catalog = getToolByName(self.context, 'portal_catalog')
        for item in catalog.searchResults({'Language': self.getLanguage()}):
            yield {
                'loc': item.getURL(),
                'lastmod': item.modified.ISO8601(),
                'changefreq': 'daily',
                #'prioriy': 0.5, # 0.0 to 1.0
            }


    def is_mobile(self):
        """
        Expose to template whether we should insert <mobile> tags.
        """
        return self.getMode() == "mobile"

    def __call__(self):
        """Checks if the sitemap feature is enable and returns it."""

        # Sitemap must be enabled in site settings
        sp = getToolByName(self.context, 'portal_properties').site_properties
        if not sp.enable_sitemap:
            raise NotFound(self.context, self.get_filename(), self.request)




        if self.request.get("uncompressed", None) != None:
            self.request.response.setHeader('Content-Type','text/xml')
            return self.uncompressed()
        else:
            self.request.response.setHeader('Content-Type', 'application/octet-stream')
            return self.generate()



