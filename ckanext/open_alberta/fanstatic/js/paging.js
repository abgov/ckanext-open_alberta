/*  Support of an "Items per Page" drop down.
 *  The dropdown sets a cookie so the selection locks.
 */
$(function() {
    var pgszSelect = $('#field-pagesize')
        .change(function() {
            docCookies.setItem('items_per_page', $(this).val());
        });
    var pgsz = docCookies.getItem('items_per_page');
    if (pgsz)
        pgszSelect.val(pgsz);
    else
        docCookies.setItem('items_per_page', pgszSelect.val());
});
