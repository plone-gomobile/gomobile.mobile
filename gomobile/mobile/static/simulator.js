// Declare namespace
if (typeof(gomobile) == "undefined") {
    gomobile = {};
}

function log(x) {
	if(console.log) {
		console.log(x);
	}
}

gomobile.simulator = {};

/**
 * Create <iframe> content for current preview to show
 */
gomobile.simulator.generateIFrame = function() {

    // Clear previous iframe
    jq("#mobile-preview-wrapper").remove();

    // Do AJAX call to bootstrap IFRAME code
    var iframe = jq("body").append('<div id="mobile-preview-wrapper" />');

    // Call view to generate snippet for us
    iframe.load("@@mobilesimulatoriframe");
}

/**
 * Open mobile preview view.
 * 
 * Assume AJAX has injected proper HTML needed to show.
 */
gomobile.simulator.open = function() {
    log("Opening");
    jq("#mobile-simulator").show();
    jq("#dark-layer").show();
    jq("#mobile-preview-wrapper").fadeIn("slow");

    // Install close handler
    jq("#preview-info,#dark-layer").click(gomobile.simulator.close);
}

/**
 * Close mobile preview view
 */
gomobile.simulator.close = function() {
    log("Closing");
    jq("#mobile-preview").hide();
    jq("div#mobile-preview-wrapper,#dark-layer").fadeOut("fast");
}

/**
 * Mobile portlet preview code
 *
 * @deprecated Replaced by the action link
 */
jq(document).ready(

    // Catch exceptions on setup
    twinapex.debug.manageExceptions( function() {
    	
	 /* To which CSS selector we bind the trigger to open the mobile preview */ 	
        var identifier = "@@mobilesimulatoriframe";
	
	// Scan through all links and see 
	var links = jq("a").filter(function() {
	       var node = jq(this);
	       var href = node.attr("href");
	       //alert("Got:" + href);
	       if(href) {
	       	       if(href.indexOf(identifier) >= 0) {
		       	  return true;
		       }
	       }
	       return false;	
	});

        jq(links).click(function(event) {

            // Remove existing framecode
	    jq("#mobile-simulator").remove();
	    
	    jq("body").append('<div id="mobile-simulator" style="display: none"></div>');
            // Extra URL source for the IFRAME from 
            var src = jq(this).attr("href");
            jq("#mobile-simulator").load(src, {}, gomobile.simulator.open);

            log(src);
	                 
           
            // Remember to return false so the default link action is not done
            return false;
        });


    })
);
