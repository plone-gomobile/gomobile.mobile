"""

    Response header manipulation after the response is complete.

    http://en.wikipedia.org/wiki/XHTML_Mobile_Profile

    Conforming doctypes:

        <!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.0//EN"
        "http://www.wapforum.org/DTD/xhtml-mobile10.dtd">

        <!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.1//EN"
        "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile11.dtd">

        <!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN"
        "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">

    http://svn.zope.de/plone.org/collective/five.caching/trunk/five/caching/event.py

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__author_url__ = "http://www.twinapex.com"
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL v2"

from zope.interface import Interface
from zope.component import adapter, getUtility
from plone.postpublicationhook.interfaces import IAfterPublicationEvent

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType

MOBILE_CONTENT_TYPE = "application/vnd.wap.xhtml+xml"

DOCSTRING_MARKER="xhtml-mobile"

def is_mobile(context, request):
    util = getUtility(IMobileRequestDiscriminator)
    flags = util.discriminate(context, request)
    return MobileRequestType.MOBILE in flags

def extract_charset(content_type):
    """
    """
    if "charset=" in content_type:
        type, charset = content_type.split("=")
        return charset
    else:
        return None

def reset_content_type_for_mobile(request, response):

    # Peek first bytes to get enough data to check the marker
    if isinstance(response.body, basestring):

        snapshot = response.body[0:160]

        # Does it look like mobile HTML
        if DOCSTRING_MARKER in snapshot:

            ct = response.getHeader("Content-type")

            charset  = extract_charset(ct)

            if charset == "None":
                # This should have been always set by
                # HTTPResponse.setBody()
                charset = "utf-8"

            # Set content type on response
            response.setHeader("Content-type", MOBILE_CONTENT_TYPE + ";charset=" + charset)

@adapter(Interface, IAfterPublicationEvent)
def set_mobile_html_content_type(object, event):

    request = event.request
    response = request.response

    # Check that we have text/html response
    if "Content-type" in response.headers:
        ct = response.getHeader("Content-type")


        if ct == "text/html" or ct == "text/xhtml":
            if is_mobile(object, request):
                reset_content_type_for_mobile(request, response)


