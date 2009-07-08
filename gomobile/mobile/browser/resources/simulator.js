
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
