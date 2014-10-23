var last_filters = {};

function filter_list(e){
    var filter = $(this).attr('data-filter');
    if (last_filters[filter] == undefined || last_filters[filter] != e.val){
        $('.table_row.hidden').removeClass('hidden');
    }
    console.log(e.val);
    if (e.val == ''){
        console.log('bella');
        last_filters[filter] = undefined;
    }
    else{
        last_filters[filter] = e.val;
    }
    var query_string = '';
    for (k in last_filters){
        if (last_filters[k] != undefined){
            query_string += '[data-'+k+'*="'+last_filters[k]+'"]';
            console.log(query_string);
        }
    }
    if (query_string != ''){
        $('.table_row').not(query_string).addClass('hidden');
    }
}

$('.to_select_2').each(function() {
    $(this).select2({
        width: '100%',
        placeholder: 'select ' + $(this).attr('id'),
        data: window[$(this).attr('id')],
    });
    $(this).on("select2-selecting", filter_list);
});
