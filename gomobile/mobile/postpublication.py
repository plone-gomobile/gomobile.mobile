"""

    Response header manipulation after the response is complete.


    http://mfabrik.com

"""

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@mfabrik.com>'
__docformat__ = 'epytext'
__copyright__ = "2009-2010 mFabrik Research Oy"
__license__ = "GPL 2"

from zope.interface import Interface
from zope.component import adapter, getUtility, getMultiAdapter
from plone.postpublicationhook.interfaces import IAfterPublicationEvent

from mobile.heurestics.contenttype import get_content_type_and_doctype, need_xhtml

from gomobile.mobile.interfaces import IMobileRequestDiscriminator, MobileRequestType, IMobileRedirector

def is_mobile(context, request):
    """
    @return: True if the served HTTP request was from the mobile site
    """
    util = getUtility(IMobileRequestDiscriminator)
    flags = util.discriminate(context, request)
    return MobileRequestType.MOBILE in flags

def need_reset(context, request):
    """ Check whether we should reset the content type for a

    Check

        1. Assumption made about user agent it wants mobile XHTML

        2. HTTP_ACCEPT header is correctly set
    """
    return need_xhtml(request)

def extract_charset(content_type):
    """
    """
    if "charset=" in content_type:
        type, charset = content_type.split("=")
        return charset
    else:
        return None

def get_suggested_content_type(request):
    """

    TODO: Not used

    @return: Content type which should be used for response, None if should not be modified
    """
    accepted = None

    # Go through possibilities
    for option in accepted:
        if option.lower() in MOBILE_CONTENT_TYPES:
            return option

    return None


def reset_content_type_for_mobile(request, response):
    """
    http://www.google.com/support/webmasters/bin/answer.py?answer=40348
    """
    ct, doctype = get_content_type_and_doctype(request)
    response.setHeader("content-type", ct)

def is_wap_accepted(request):
    """
    Puke on WAP. Blaaarg.

    application/vnd.wap.xhtml+xml"
    """

def get_context(object):
    """ Post-publication hook object can be either view or context object.

    Try extract context object in meaningful manner.

    @param object: View instance of content item instance
    """

    # Get context attribute or return the object itself if does not exist
    context = getattr(object, "context", object)
    return context

@adapter(Interface, IAfterPublicationEvent)
def set_mobile_html_content_type(object, event):
    """
    Post publication hook which sets HTML content type so that the page is understood as a mobile page.

    NOTE: This should be done for Googlebot and other mobile aware search bots only!
    Various *real* mobile handsets
    blow up if you try to feed them anything else beside text/html
    (iPhone - I am looking at you).
    """
    request = event.request
    response = request.response

    # Check that we have text/html response
    ct = response.getHeader("Content-type")

    if ct is not None:
        if ct.startswith("text/html") or ct.startswith("text/xhtml"):
            context = get_context(object)

            if is_mobile(context, request):
                if need_reset(context, request):
                    reset_content_type_for_mobile(request, response)


@adapter(Interface, IAfterPublicationEvent)
def mobile_redirect(object, event):
    """ Redirect mobile users to mobile site using gomobile.mobile.interfaces.IRedirector.

    Note: Plone does not provide a good hook doing this before traversing, so we must
    do it in post-publication. This adds extra latency, but is doable.
    """

    request = event.request
    response = request.response
    context = object

    #print "Got UA:" + str(request["HTTP_USER_AGENT"])

    redirector = getMultiAdapter((context, request), IMobileRedirector)

    ct = response.getHeader("Content-type")
    #print "Got ct:" + ct

    # Do not do redirects for images, CSS or other non-content requests
    # note that ct string may be text/html;charset=utf-8

    if ct is not None:
        if ct.startswith("text/html") or ct.startswith("text/xhtml"):
            #print "Intercepting"
            if redirector.intercept():
                # Redirect happened
                # Override payload so that we don't send extra data to mobile
                #print "Redirected"
                response.body = ""
                response.setHeader("Content-length", 0)

