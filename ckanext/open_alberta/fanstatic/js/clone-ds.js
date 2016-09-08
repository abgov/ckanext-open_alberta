$(function() {
    /* This submits dataset clone request via Ajax.
     * It has to be done this way because the dataset view page has javascript tabs,
     * unlike vanilla CKAN.
     * */
    $('#id-clone-ds-form button[type=submit]').click(function(e) {
        console.log('clone clicked...');
        var url = $('#id-clone-ds-form').attr('action');
        var titleInp = $('#field-title');
        var urlInp = $('#field-name');
        $('#id-clone-ds-form .top-error-msg').text('').hide();
        titleInp.parent().removeClass('error').find('span.error-block').remove();
        urlInp.parent().removeClass('error').find('span.error-block').remove();
        $.post(url,
            { title: $('#field-title').val(),
              name: $('#field-name').val() },
            function(data) {
                if (data.status == 'success')
                    window.location.href = data.redirect_url;
                else if (data.status == 'error') {
                    if (data.errorMessage) {
                        $('#id-clone-ds-form .top-error-msg').text(data.errorMessage).show();
                    }
                    else {
                        if (data.errors.title)
                            titleInp.after('<span class="error-block">'+data.errors.title[0]+'</span>')
                                    .parent().addClass('error');
                        if (data.errors.name) {
                            // URL input is initially hidden. Need to show.
                            var editBtn = titleInp.parent().find('.btn-mini');
                            if (editBtn.length)
                                $(editBtn[0]).click();

                            urlInp.after('<span class="error-block">'+data.errors.name[0]+'</span>')
                                  .parent().addClass('error');
                        }
                    }
                }
                else
                    ; // TODO: Unexpected server response
            });
        e.preventDefault();
    });
});
