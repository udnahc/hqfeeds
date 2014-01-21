$('a.feedlink').on('click', function(event) {
    event.preventDefault();
    var dataUrl = event.currentTarget.getAttribute("data-url") || "",
        dataLabel= event.currentTarget.getAttribute("data-label") || ""
    fetch_feeds(dataUrl, dataLabel);
});