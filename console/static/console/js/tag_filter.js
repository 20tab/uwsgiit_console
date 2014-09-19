var last_tag;
$(document).on('click', '.tag_filter', function(e) {
    e.preventDefault();
    var filter = $(this).attr('data-filter');
    $('.domain_row.hidden').removeClass('hidden');
    if (last_tag == undefined || last_tag != filter){
        $('.domain_row').not('[data-category*="'+filter+'"]').addClass('hidden');
        $('.tag_filter.active').removeClass('active');
        $('.tag_filter[data-filter="'+filter+'"]').addClass('active');
        last_tag = filter;
    } else {
        $('.tag_filter[data-filter="'+filter+'"]').removeClass('active');
        last_tag = undefined;
    }
});
