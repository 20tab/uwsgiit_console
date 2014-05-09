jQuery(function($){

    $('button.submit-container-form').on('click', function(){
        $('#id_action').val($(this).attr('id'));
        $('#container-form').submit();
    });

    $('a.submit-container-form').on('click', function(e){
        e.preventDefault();
        var id = $(this).data('id');
        $('#id_'+$(this).data('field')).val(($('#'+id).text()));
        $('#id_action').val($(this).data('action'));
        $('#container-form').submit();
    });



});