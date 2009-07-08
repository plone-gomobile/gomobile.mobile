"""

    Mobile site testing utils
   
   These are in separate file, so that third party products can use them easily.
"""

__license__ = "GPL 2.1"
__copyright__ = "2009 Twinapex Research"

def setDiscriminateMode(request, mode):
    """ Spoof the discrimination mode. 
    
    Poke HTTP request internals to look like it is directed
    to domain name based discriminating.
    
    @param mode: 'mobile' or 'web'
    """
    
    def setURL(url):
        request.other["URL"] = url
        request.other["ACTUAL_URL"] = url        
        request.other["SERVER_URL"] = url        
        
    if mode == "mobile":
        host = "mobile.nohost"
    elif mode == "preview":
        host = "preview.nohost"        
    elif mode == "web":
        host = "web.nohost"
    else:
        raise RuntimeError("Unknown mode:" + mode)
    
    setURL("http://" + host)
    request.environ["HTTP_HOST"] = host
    
