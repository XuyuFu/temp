function addComment(activity_id) {
    var itemTextElement = document.getElementById("comment-"+activity_id);
    console.log(itemTextElement);
    var itemTextValue   = itemTextElement.value;
    console.log(itemTextValue);
    itemTextElement.value = '';
    displayError_comment('');


    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        var response = JSON.parse(req.responseText);
        console.log( typeof (response));
        console.log("return");
        console.log(response);
        var fix_response = response;
        if (Array.isArray(fix_response)) {
            console.log("is array");
            updateCommentList(fix_response);
            console.log("heiheihei");
        } else {
            console.log("is not array");
            displayError_comment(fix_response.error);
        }
    }

    req.open("POST", "/add-comment", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.send("comment="+itemTextValue+"&activity_id="+activity_id+"&csrfmiddlewaretoken="+getCSRFToken());

}

function addProgress(activity_id) {
    var itemTextElement = document.getElementById("progress-"+activity_id);
    console.log(itemTextElement);
    var itemTextValue   = itemTextElement.value;
    console.log(itemTextValue);
    itemTextElement.value = '';
    displayError_progress('');


    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        var response = JSON.parse(req.responseText);
        console.log( typeof (response));
        console.log("return");
        console.log(response);
        var fix_response = response;
        if (Array.isArray(fix_response)) {
            console.log("is array");
            updateProgressList(fix_response);
            console.log("heihei");
        } else {
            console.log("is not array");
            displayError_progress(fix_response.error);
        }
    }
    req.open("POST", "/add-progress", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    console.log("before hah");
    req.send("progress="+itemTextValue+"&activity_id="+activity_id+"&csrfmiddlewaretoken="+getCSRFToken());

}


function updateCommentList(items) {
    // Removes the old to-do list items

    var post_id = items[0].post_id;
    var list    = document.getElementById("comment-list-"+post_id);
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
        var list    = document.getElementById("comment-list-"+post_id);
        var newComment = document.createElement("li");
        newComment.innerHTML=content;
        console.log(post_id);
        console.log(content);
        if(list == null)
            continue;
        list.appendChild(newComment);
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