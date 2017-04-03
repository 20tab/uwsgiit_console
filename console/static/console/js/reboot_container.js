$('#reboot-container').on('click', function(e){
    e.preventDefault();
    var btn = $(this);
    $.ajax({
        type: "POST",
        url: reboot_container_url,
        dataType: 'json',
        data: {csrfmiddlewaretoken: csrf_token},
        beforeSend:function(){
            btn.button('loading');
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
            btn.button('reset');
        }
    });
});
