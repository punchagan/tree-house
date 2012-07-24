function commentsInit(pageURL) {
    $(".comments .collapse").click(function() {
        $(this).addClass('hidden');
        $(this).parent().find('.uncollapse').removeClass('hidden');
        $(this).parent().parent().find('.com-body').slideUp("fast");
        $(this).parent().parent().parent().find('.com-children').slideUp("fast");
        return false;
    });

    $(".comments .uncollapse").click(function() {
        $(this).addClass('hidden');
        $(this).parent().find('.collapse').removeClass('hidden');
        $(this).parent().parent().find('.com-body').slideDown("fast");
        $(this).parent().parent().parent().find('.com-children').slideDown("fast");
        return false;
    });

    $(".comments .comment-reply").click(function() {
        var cfooter = $(this).parent();
        $('#newcomment input[name="parent_id"]').val(cfooter.attr('data-id'));
        $('#newcomment input[name="edit_id"]').val('');
        $("#toplevel-comment").removeClass('hidden');
        $("#comment-submit").val("Reply"); // i18n gotcha
        cfooter.after($("#newcomment"));
        $("#newcomment textarea").focus();
        return false;
    });

    $("#toplevel-comment a").click(function() {
        $('#newcomment input[name="parent_id"]').val('');
        $('#newcomment input[name="edit_id"]').val('');
        $("#comment-submit").val("Post comment"); // i18n gotcha
        $(this).parent().after($("#newcomment"));
        $(this).parent().addClass('hidden');
        $("#newcomment textarea").focus();
        return false;
    });

    $(".comments .comment-delete").click(function() {
        var cfooter = $(this).parent();
        $('#delcomment input[name="comment_id"]').val(cfooter.attr('data-id'));
        $("#delcomment").removeClass('hidden').hide().insertAfter(cfooter).slideDown("fast");
        return false;
    });

    $("#comment-delete-cancel").click(function() {
        $("#delcomment").slideUp("fast");
        return false;
    });

    $(".comments .comment-edit").click(function() {
        var cfooter = $(this).parent();
        var cid = cfooter.attr('data-id');
        $("#newcomment textarea").val("Loading..."); // i18n gotcha
        $.getJSON(pageURL+'/comments/'+cid+'/json', function(data) {
            $("#newcomment textarea").val(data.message);
            });
        $('#newcomment input[name="parent_id"]').val('');
        $('#newcomment input[name="edit_id"]').val(cid);
        $("#toplevel-comment").removeClass('hidden');
        $("#comment-submit").val("Save changes"); // i18n gotcha
        cfooter.after($("#newcomment"));
        $("#newcomment textarea").focus();
        return false;
    });
};

// Add datepicker to all date-fields
$(document).ready(function()
    {
      var cur = new Date();
      var date = cur.getFullYear() + "-" + (cur.getMonth()+1) + "-" + cur.getDate();
      $(".date-field").val(date).datepicker({format: "yyyy-mm-dd"});
    }
);
