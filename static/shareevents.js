$('a.share').on('click', function(event) {
    event.preventDefault();
    var urlAttr = event.currentTarget.getAttribute("data-url") || "",
        titleAttr = event.currentTarget.getAttribute("data-title") || "",
        socialAttr = event.currentTarget.getAttribute("data-social") || "";
    if(urlAttr==null) {
        return;
    }
    var f = 600, g = 600, j = screen.height, c = screen.width, l = Math.round((c / 2) - (f / 2)), d = 0, popupObj;
    if (j > g) {
        d = Math.round((j / 2) - (g / 2));
    }
    popupObj = window.open("about:blank", "", "left=" + l + ",top=" + d + ",width=600,height=600,personalbar=0,toolbar=0,scrollbars=1,resizable=1");
    if(popupObj == null) {
        return;
    }
    popupObj.focus();
    if(socialAttr == 'pinterest') {
         popupObj.location = "http://pinterest.com/pin/create/button/?url=" + encodeURIComponent(urlAttr) + "&media=" + encodeURIComponent(titleAttr);
    }
    else if (socialAttr == 'linkedin') {
        popupObj.location = "http://www.linkedin.com/shareArticle?mini=true&url=" + encodeURIComponent(urlAttr);
    }
    else if (socialAttr == "gplus") {
        popupObj.location = "https://plusone.google.com/_/+1/confirm?hl=en&url=" + encodeURIComponent(urlAttr);
    }
    else if (socialAttr == "tw") {
        popupObj.location = "http://twitter.com/share?url=" + encodeURIComponent(urlAttr);
    }
    else if (socialAttr == "fb") {
        popupObj.location = "http://www.facebook.com/sharer.php?u=" + encodeURIComponent(urlAttr) + "&t=" + encodeURIComponent(titleAttr);
    }
    else if (socialAttr == "pocket") {
        popupObj.location = "http://getpocket.com/edit.php?url=" + encodeURIComponent(urlAttr);
    }
    else {
        popupObj.location = ""; // todo for our app like
    }
});