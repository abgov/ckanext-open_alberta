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
});
