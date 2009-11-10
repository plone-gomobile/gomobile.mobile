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
from zope.component import adapter
from plone.postpublicationhook.interfaces import IAfterPublicationEvent

CONTENT_TYPE = "application/vnd.wap.xhtml+xml"

DOCSTRING_MARKER="xhtml-mobile"

@adapter(Interface, IAfterPublicationEvent)
def set_mobile_html_content_type(object, event):
    pass
    return

    request = event.request
    response = event.request.response


    # Check that we have text/html response
    if "Content-type" in response.headers:
        ct = response.headers["Content-type"]
        pass

        if ct == "text/html":
            # Peek first bytes to get enough data to check the marker
            pass

    # Does it look like mobile HTML

    # Set content type on response
