var most_recent_date = "1 1, 1223 00:00:00";
var new_most_recent_date = most_recent_date;

// Sends a new request to update the to-do list
function getList() {
    $.ajax({
        url: "/payfun/getFollowerPostsJson",
        dataType : "json",
        data: "most_recent_date="+most_recent_date,
        success: function(response) {
            if (Array.isArray(response)) {
                updatePosts(response);
                $.ajax({
                    url: "/payfun/getFollowerCommentsJson",
                    dataType : "json",
                    data: "most_recent_date="+most_recent_date,
                    success: function(response) {
                        updateComments(response);
                        most_recent_date = new_most_recent_date;
                    }
                });
            } else {
                displayError(response.error);
            }
        }
    });
}

function updatePosts(items) {
    // Removes the old posts
    // $("li").remove();

    // Adds new posts to the list

    $(items).each(function() {

        var datePost = new Date(this.created);
        var dateNewMostRecent = new Date(new_most_recent_date);

        if (datePost > dateNewMostRecent) {
            new_most_recent_date = this.created;
        }

        $("#posts").prepend(

            `<div class="jumbotron">  
                <div class="postings" id=` + this.post_id +`>
                    <h1>` + this.header +`</h1>
                    <h7>Posted by: <a class="mt-0" href="profile`+ this.posted_by_id + `">` + this.posted_by_name + `</a></h7>
                    <h8>at ` + this.created + `</h8>
                    <p>` + this.text + `</p>
                </div>

                <hr>

                <div id="comments_for_` + this.post_id +`">
                </div>

                <div class="card my-4 comment_input">
                    <h5 class="card-header">Leave a Comment:</h5>
                    <div class="card-body">
                        <form action="" method="post">
                            <div class="form-group">
                                <textarea class="form-control" id="new_text_` + this.post_id + `" name="text" rows="1"></textarea>
                            </div>
                            <button type="submit" id="comment_button_` + this.post_id + `" class="btn btn-primary" onclick="addComment(this.id)">Submit</button>
                            <script>
                                document.getElementById("comment_button_` + this.post_id + `").addEventListener("click", function(event){
                                    event.preventDefault()
                                });
                            </script>
                        </form>
                    </div>
                </div>

            </div>`

        );
    });

}

function updateComments(items) {

    // Adds new comments to the list
    $(items).each(function() {
        var tempId = "#comments_for_" + this.post_id;
        var commentsDiv = $(tempId);

        commentsDiv.append(
            `<div>
                <div>
                  <a class="mt-0" href="profile`+ this.commented_by_id + `">` + this.commented_by_name + `</a>
                  <h8>at ` + this.created + `</h8>
                   <p>` + this.text + `</p>
                </div>
             </div>`
        );

        var commentPost = new Date(this.created);
        var dateNewMostRecent = new Date(new_most_recent_date);

        if (commentPost > dateNewMostRecent) {
            new_most_recent_date = this.created;
        }
    });

}



function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
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

function addPost() {
    var headerElement = $("#new_header");
    var header = headerElement.val();
    var textElement = $("#new_text")
    var text = textElement.val();

    $.ajax({
        url: "/psyfun/add-post",
        type: "POST",
        xhrFields: {
            withCredentials: true
        },
        data: "header="+header+"&text=" + text + "&most_recent_date=" + most_recent_date + "&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: function(response) {
            if (Array.isArray(response)) {
                updatePosts(response);
                most_recent_date = new_most_recent_date;
            } else {
                displayError(response.error);
            }
        }
    });
}

function addComment(buttonId) {
    /*var thisElement = $(this)
    var buttonId = thisElement.attr('id')*/
    var postId = parseInt(buttonId.substring(15));
    var thisElement = $(this);
    var buttonId = thisElement.attr('id');
    var textElement = $("#new_text_" + postId);
    // var textElement = $("#new_text_" + buttonId)
    var text = textElement.val();

    console.log("addComment");

    $.ajax({
        // url: "/addComment",
        url: "/socialnetwork/add-comment",
        type: "POST",
        xhrFields: {
            withCredentials: true
        },
        data: "post_id="+postId+"&text=" + text + "&most_recent_date=" + most_recent_date + "&csrfmiddlewaretoken="+getCSRFToken(),
        // data: "text=" + text +"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: function(response) {
            console.log("update")
            if (Array.isArray(response)) {
                updateComments(response);
                most_recent_date = new_most_recent_date;
            } else {
                displayError(response.error);
            }
        }
    });
}



// The index.html does not load the list, so we call getList()
// as soon as page is finished loading
window.onload = getList;

// causes list to be re-fetched every 5 seconds
window.setInterval(getList, 5000);