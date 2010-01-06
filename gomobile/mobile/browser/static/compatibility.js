/**
 * XXX NOT CURRENTLY NEEDED
 *
 * Compatibility layer between different mobile phones.
 *
 * Allow certain behavior (like phone number links) for well on every phone.
 *
 * Depends on this script unless you remove exception wrapper:
 *
 * http://snipplr.com/view/10137/exception-manager-for-dom-event-handlers--no-more-silent-failures/
 *
 */

// Declare namespace
if (gomobile === undefined) {
	gomobile = {};
}

gomobile.compatiblity = {};

gomobile.compatibility.isiPhone = function() {
	return navigator.userAgent.match(/iPhone/i);
}

/**
 * Maps wp://wa links compatible to iPhone
 *
 * http://mobility.mobi/showthread.php?t=29269.
 *
 * 1) Assume all links have class "phone-number"
 *
 * 2) If in iPhone, rewrite these <a> tags
 *
 * You need to present phone number in your HTML code:
 *
 * <a class="phone-number" href="wtai://wp/mc;+358401231234">+358 40 123 1234</a>
 *
 * which will be converted for iPhone
 *
 * <a href="tel:+358401231234">+358 40 123 1234</a>
 *
 *
 */
gomobile.compatibility.fixPhoneNumberLinks = function() {
	if(gomobile.compatibility.isiPhone()) {

		var wtai_prefix = "wtai://wp/mc;";

		jq(".phone-number").each( function() {
			var elem = jq(this);
			var number = elem.attr("href");
			number = number.substring(wtai_prefix.length);
			elem.attr("href", "tel:" + number);
		});
	}
}

/**
 * Mobile portlet preview code
 *
 * @deprecated Replaced by the action link
 */
jq(document).ready( function(){

	// Catch exceptions on setup
	twinapex.debug.manageExceptions(function(){
		gomobile.compatibility.fixPhoneNumberLinks();
	});
});
