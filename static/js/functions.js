jQuery(function($){

    $('#update-container').on('click', function(){
        $(this).button('loading');
        $('#container-form').submit();
    });

    $('#add-key').on('click', function(){
        $(this).button('loading');
        $('#id_action').val($(this).attr('id'));
        $('#ssh-form').submit();
    });

    $('a.submit-container-form').on('click', function(e){
        e.preventDefault();
        var id = $(this).data('id');
        $('#id_key').val($('#'+id).text());
        $('#id_action').val($(this).data('action'));
        $('#ssh-form').submit();
    });
});
