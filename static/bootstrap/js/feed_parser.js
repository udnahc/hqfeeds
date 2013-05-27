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

function mark_read(url,class_name) {
    $("#"+class_name).css({'background-color':"#DFEFF2"})
}

function like_link(url, feed_name) {
    $.ajax({
	    type:"POST",
		url: "/like/",
		data: {"url":url, "feed_name":feed_name},
		success: function(return_value) {
		$("#right-nav").html(return_value);
	    }
	});
}

function read_later() {
    alert('Read this link later');
}

function share() {
    alert('Share this link');
}

function edit_tags() {
    alert('Edit tags for this link');
}