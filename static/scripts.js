$(document).ready(function(){
    $("#unfollow").hide();
    $("#follow").click(function(){
        $("#follow").hide();
        $("#unfollow").show();
    });
    $("#unfollow").click(function(){
        $("#unfollow").hide();
        $('#follow').show();
    });
});