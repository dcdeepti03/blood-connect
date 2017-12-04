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