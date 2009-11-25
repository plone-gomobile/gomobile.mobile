// Declare namespace
if (typeof(gomobile) == "undefined") {
    gomobile = {};
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
 * Open mobile preview view
 */
gomobile.simulator.open = function() {

    gomobile.simulator.generateIFrame();
    jq("#dark-layer").show();
    jq("div#mobile-preview-wrapper").fadeIn("slow");

}

/**
 * Close mobile preview view
 */
gomobile.simulator.close = function() {
    jq("div#mobile-preview-wrapper,#dark-layer").fadeOut("fast");
}

/**
 * Boostrap simulator click handlers
 */
jq(document).ready(

    // Catch exceptions on setup
    twinapex.debug.manageExceptions( function() {

        jq("a.mobile-preview").click(function(event) {
            gomobile.simulator.open()
            // Remember to return false so the default link action is not done
            return false;
        });

        // Close
        jq("#preview-info").click(function(event){
            gomobile.simulator.close();
            // Remember to return false so the default link action is not done
            return false;
        });

    })
);


/**
 * Mobile portlet preview code
 *
 * @deprecated Replaced by the action link
 */
jq(document).ready(

    // Catch exceptions on setup
    twinapex.debug.manageExceptions( function() {

        jq("a.open-mobile-preview").click(function(event) {
            jq("#dark-layer").show();
            var mobileSrc = jq("#mobile-preview-url").text();
            jq("iframe").attr("src", mobileSrc );
            jq("div#mobile-preview-wrapper").fadeIn("slow");

            // Remember to return false so the default link action is not done
            return false;
        });
        // Close
        jq("#preview-info").click(function(event){
            jq("div#mobile-preview-wrapper,#dark-layer").fadeOut("fast");

            return false;
        });

    })
);
