$(function() {
    $('#clone-btn').click(function() {
        var icon = $('i', this);
        if (icon.hasClass('icon-caret-down')) {
            $('fieldset.clone').show()
                               .find('input:eq(0)').focus();
            icon.removeClass('icon-caret-down')
                .addClass('icon-caret-up');
        }
        else {
            $('fieldset.clone').hide();
            icon.removeClass('icon-caret-up')
                .addClass('icon-caret-down');
        }
    });
    /* This submits dataset clone request via Ajax.
     * It has to be done this way because the dataset view page has javascript tabs,
     * unlike vanilla CKAN.
     * */
    $('#clone-form button[type=submit]').click(function(e) {
        var url = $('#clone-form').attr('action');
        var titleInp = $('#field-title');
        var urlInp = $('#field-name');
        $('#clone-form .top-errors').text('').hide();
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
                        $('#clone-form .top-errors').text(data.errorMessage).show();
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
