jQuery(function($){

    $('#update-container').on('click', function(e){
        e.preventDefault();
        $(this).button('loading');
        $('#container-form').submit();
    });

    $('#update-and-reboot-container').on('click', function(e){
        e.preventDefault();
        $(this).button('loading');
        var form = $('#container-form');
        form.find('input[name="reboot"]').attr('value', 'True')
        form.submit();
    });

    $('#add-key').on('click', function(e){
        e.preventDefault();
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

    var last_tag;
    $('.tag_filter').on('click', function(e) {
        e.preventDefault();
        var filter = $(this).attr('data-filter');
        $('.table_row.hidden').removeClass('hidden');
        if (last_tag == undefined || last_tag != filter){
            $('.table_row').not('[data-category*="'+filter+'"]').addClass('hidden');
            $('.tag_filter.active').removeClass('active');
            $('.tag_filter[data-filter="'+filter+'"]').addClass('active');
            last_tag = filter;
        } else {
            $('.tag_filter[data-filter="'+filter+'"]').removeClass('active');
            last_tag = undefined;
        }
    });


    function fill_related(elem){
        if(elem != undefined){
            $.ajax({
                url: elem.attr('data-url'),
                dataType: 'json',
                success: function(data){
                    elem.html(data.rendered)
                }
            })
        }
    }

    fill_related($('#table-domains-in-container'));
    fill_related($('#table-containers-per-domain'));

    $('select').select2({
        width: '200px'
    });
});
