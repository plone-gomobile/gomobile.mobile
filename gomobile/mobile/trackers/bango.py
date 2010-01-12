"""

    Viewlets for mobile tracking codes.

    On mobile sites, Javascript based tracking (Google analytics) cannot be used.

"""

__license__ = "GPL 2"
__copyright__ = "2009 Twinapex Research"

import md5
import urllib

from Acquisition import aq_inner
import zope.interface

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from gomobile.mobile.interfaces import IMobileTracker

from five import grok


class BangoTracker(object):
    """ Bango tracking code generator.

    https://bango.com

    Bango inserts a hidden image which contains the page URI and referer.

    Set "Page tracking code" given by Bango to mobile_properties.

    Example::

        <%
        //********** Bango Page tracking code - JSP **********

        //Specify the unique page name variable
        //CHANGE THIS VALUE FOR EACH DIFFERENT PAGE YOU ADD THE CODE TO
        String pageName = "example_page_title";

        //Extract the referrer from the server variables
        String referrer = request.getHeader("Referer");
        String ba_referrer = "";

        //Check to ensure there is a value in the referrer
        if(referrer != null && !referrer.isEmpty())
        {
          ba_referrer = "&amp;referrer=" + java.net.URLEncoder.encode(referrer, "UTF-8");
        }

        //Extract the query string if available
        String queryString = request.getQueryString();

        //Ensure pageName is URL Encoding safe
        pageName = java.net.URLEncoder.encode(pageName, "UTF-8");

        //Create the image source url
        String imageSrcURL = "http://bango.net/id/111555005278.gif?page=" + pageName;

        //Check to ensure there is a value in the referrer and add to the image source url
        if(ba_referrer != null && !ba_referrer.isEmpty())
        {
          imageSrcURL += ba_referrer;
        }

        //Check to ensure there is a value in the query string and add to the image source url
        if(queryString != null && !queryString.isEmpty())
        {
          imageSrcURL += "&amp;" + queryString;
        }
        %>

        <div>
          <img src="<%= imageSrcURL%>" alt="" height="1" width="1" />
        </div>

    """

    zope.interface.implements(IMobileTracker)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def track(self, trackingId, debug):

        referer = self.request.get_header("referer", "")

        # TODO: This is virtual hostless path... strip site instance name here
        pageName = self.request["PATH_TRANSLATED"]

        queryString = self.request["QUERY_STRING"]

        imageSrcURL = "http://bango.net/id/111555005278.gif?page=" + pageName

        if referer != "":
            ba_referrer = "&amp;referrer=" + urllib.urlencode({"referer":referer})
            imageSrcURL += ba_referrer


        img = """<img class="tracker" src="%s" alt="" height="1" width="1" />""" % imageSrcURL

        return img