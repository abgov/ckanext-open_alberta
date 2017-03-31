function hide_filters_on_body_click() {
    $('body').off('click', hide_filters_on_body_click);
    $('.mobile-filters-panel')
        .animate({'margin-left': '-350px'}, 
                 {duration: 300,
                  complete: function() { $(this).hide() }});
}

$(function() {
    // It seems AB Gov version of bootstrap doesn't work well with the one from CKAN.
    // Toggle buttons don't work properly.
    // The below tries to fix those problems.
    // The code assumes markup from dropdown bootstrap example.
    $('.dropdown-toggle').click(function() {
        $(this).parent().toggleClass('open');
    });

    // Move the filters panel to the main column and shift it to the left so it's ready to slide in.
    // Mobile view only.
    var mfp = $('.catalogue div.secondary').clone(true, true);
    mfp.prependTo('body')
       .addClass('mobile-filters-panel')
       .click(function(e) { 
           // prevent tap/click on filters panel to get to the body element
           // e.stopPropagation(); 
       });

    $('#show-filters').click(function() {
        $('.mobile-filters-panel')
            .show()
            .animate({'margin-left': 0}, 300, function() {
                $('body').on('click', hide_filters_on_body_click);
            });
    });

    $('h3 .fa-close').click(hide_filters_on_body_click);
});
