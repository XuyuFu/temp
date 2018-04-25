var lastUpdateTime = '1970-01-01 00:00:00.00';

function addComment(activity_id) {
    var itemTextElement = document.getElementById("comment-" + activity_id);
    console.log(itemTextElement);
    var curPage = window.location.href.split("/")[3];
    console.log(curPage);
    var itemTextValue = itemTextElement.value;
    console.log(itemTextValue);
    itemTextElement.value = '';
    displayError_comment('');
    alert("1");


    if (itemTextValue != "") {
        $.ajax({
            url: "/add-comment",
            type: "POST",
            data: "comment=" + itemTextValue + "&activity_id=" + activity_id + "&last_update_time=" + lastUpdateTime + "&cur_page=" + curPage + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: function (response) {
                updateHelper(response);
                alert("2");
            }
        });
    }
}

function updateHelper(response) {
    alert("3");
    var comments = JSON.parse(response['comments']);
    console.log(comments);
    var progress = JSON.parse(response['progress']);
    console.log(progress);
    lastUpdateTime = response['last_update_time'];

    $(progress).each(function() {
         var target = "#progress-list-" + this.post_id;
         $(target).append(this.html);
    });

    $(comments).each(function() {
        var target = "#comment-list-" + this.post_id;
        $(target).append(this.html);
        //alert("00");
    });
    alert("4");
}

function addProgress(activity_id) {
    //alert("000");
    var itemTextElement = document.getElementById("progress-"+activity_id);
    var curPage = window.location.href.split("/")[3];
    var itemTextValue   = itemTextElement.value;
    itemTextElement.value = '';
    displayError_progress('');
    //alert("111");
    if (itemTextValue != "") {
        $.ajax({
            url: "/add-progress",
            type: "POST",
            data: "progress=" + itemTextValue + "&activity_id=" + activity_id + "&last_update_time=" + lastUpdateTime + "&cur_page=" + curPage + "&csrfmiddlewaretoken=" + getCSRFToken(),
            dataType: "json",
            success: function (response) {
                //alert("222");
                updateHelper(response);

            }
        });
    }


}



function updateProgressList(items) {
    // Removes the old to-do list items

    var post_id = items[0].post_id;
    var list    = document.getElementById("progress-list-"+post_id);
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }

    for(var i=0; i<items.length;i++)
    {
        console.log(items[i]);
        var post_id = items[i].post_id;
        console.log(post_id);
        var content = items[i].html;
        console.log(content);
        console.log(typeof (content));
        var list    = document.getElementById("progress-list-"+post_id);
        var newComment = document.createElement("li");
        newComment.innerHTML=content;
        console.log(post_id);
        console.log(content);
        if(list == null)
            continue;
        list.appendChild(newComment);
    }
}

function test(activity_id) {
    alert("hah");

}

function displayError_comment(message) {
    var errorElement = document.getElementById("error-comment");
    errorElement.innerHTML = message;
}

function displayError_progress(message) {
    var errorElement = document.getElementById("error-progress");
    errorElement.innerHTML = message;
}

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}

function getProgressComment() {

    var tmp = window.location.href.split("/");
    console.log(tmp);
    console.log(tmp);
    console.log(tmp);
    console.log(tmp);
    var curPage = window.location.href.split("/")[3];
    var id = "0";
    if(window.location.href.split("/").length>4)
        id = window.location.href.split("/")[4];
        console.log(id);
        console.log(id);
        console.log(id);
        console.log(id);

    $.ajax({
        url: "/get-post-comment",
        dataType: "json",
        data: "last_update_time="+lastUpdateTime+"&cur_page=" + curPage + "&activity_id="+ id + "&csrfmiddlewaretoken=" + getCSRFToken(),
        success: updateHelper
    });
}



function initial(){
    //alert("11111111");
    var curPage = window.location.href.split("/")[3];
    if(window.location.href.split("/").length>4)
        id = window.location.href.split("/")[4];
    //alert("11111111.55555555555");
     $.ajax({
        url: "/getAllProgressAndComment",
        dataType: "json",
        data: "&cur_page=" + curPage + "&activity_id="+ id + "&csrfmiddlewaretoken=" + getCSRFToken(),
        success: updateHelper
    });

}
window.onload = initial;

//window.setInterval(getProgressComment, 5000);