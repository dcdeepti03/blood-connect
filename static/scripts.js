function archiveMessage(message_id) {
    $.ajax({
        url: ['/archive-request', message_id].join('/'),
        type: "DELETE",
        success: function(){

            $("#" + message_id).html("<div class='alert alert-success'>Message archived</div>");
            setTimeout(function(){
                $("#" + message_id).remove();
            }, 3000)
        },
        failure: function() { alert('An error occurred');},
        error: function() { alert('An error occurred');}
    });
}

$(document).ready(function(){
    var currentLocation = window.location.href;
    var home = $("#home");
    var register = $("#register");
    var notify = $("#notify");
    if(currentLocation.indexOf("register-donor") !== -1){
        register.addClass("active");
    } else if(currentLocation.indexOf("notify-donors") !== -1) {
        notify.addClass("active");
    } else {
        home.addClass("active");
    }
});