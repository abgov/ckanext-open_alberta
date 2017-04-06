/*
 * Show/hide Redirect URL input based on the value of homepage drop-down
 */

$(function() {
    var hpstyle = $('#field-ckan-homepage-style');
    if (hpstyle.val() != '301')
        $('#field-ckan-abgov-301-url').parent().parent().hide();
    else
        $('#field-ckan-abgov-301-url').parent().parent().show();
    hpstyle.on('change', function() {
        var urlfld = $('#field-ckan-abgov-301-url');
        if ($(this).val() == '301')
            urlfld.parent().parent().show();
        else {
            urlfld.val('').parent().parent().hide();
        }
    });

    var cb = $('#field-ckan-abgov-display-notice');
    // A standard checkbox doesn't bind it's value to the checked state
    cb.change(function() {
         var me = $(this);
         me.val(me.is(':checked')? 'True': 'False');
       })
      .prop('checked', cb.val()=='True');
});
