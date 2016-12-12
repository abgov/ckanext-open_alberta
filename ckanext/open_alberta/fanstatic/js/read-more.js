/*  
 *  Replace short version of a content with the contents of the next element.
 */
$(function() {
    $('a.read-more').click(function() {
        console.log('boo!');
        $(this).closest('.short').hide().next().show();
        return false;
    });
});
