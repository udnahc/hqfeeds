function fetch_feeds(dataUrl, dataLabel) {

$.ajax ({
    url: "http://127.0.0.1:5000/fetch_feeds_for_url",
    type: "POST",
    data: JSON.stringify({ feed_uri: dataUrl, feed_label: dataLabel }),
    contentType: "application/json; charset=utf-8",
    success: function( msg ){
        $("#feed_content").html(msg);
    }
});
}