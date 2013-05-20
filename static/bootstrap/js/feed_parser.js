function show_feed(url_label,url) {
    $.ajax({
	    type:"POST",
		url: "/show_feed_entries/",
		data: {"url":url, "feed_name":url_label},
		beforeSend: function() {
		$("#right-nav").html("<div class='alert alert-info'>Loading feed for " + url_label + "</div>");
	    },
		success: function(return_value) {
		$("#right-nav").html(return_value);
	    }
	});
}