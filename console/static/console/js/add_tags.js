var add_tag_btn = '<button type="submit" class="glyphicon glyphicon-floppy-save"></button>';
var loading_icon = '<img src="' + static_url + 'select2/select2-3.4.5/select2-spinner.gif" alt="Loading..." />';
$('.add-domain-form').on('submit', function(e){
    e.preventDefault();
    var form = $(this);
    $.ajax({
        type: form.attr('method'),
        url: form.attr('action'),
        data: form.serialize(),
        dataType: 'json',
        beforeSend:function(){
            form.children('button[type="submit"]').remove();
            form.append(loading_icon);
        },
        success:function(data){
            if ('error' in data){
                alert('An error occurred: '+ data['error']);
            }
        },
        error:function(){
            alert('An error occurred. Try that again in a few moments.');
        },
        complete:function(){
            form.children('img').remove();
            form.append(add_tag_btn);
        }
    });
});
