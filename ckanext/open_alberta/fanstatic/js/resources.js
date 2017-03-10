function hide_filters_on_body_click() {
    $('body').off('click', hide_filters_on_body_click);
    $('.wrapper-resources div.secondary').animate({'margin-left': '-350px'}, 300);
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
    if ($('#show-filters').css('display') != 'none') {
        $('.wrapper-resources div.secondary')
            .addClass('mobile-filters-panel')
            .appendTo('.wrapper-resources > .primary')
            /*.css({'position': 'absolute',
                  'top': '0px',
                  'left': '0px',
                  'padding': '0px',
                  'margin-left': '-350px'}) */
            .click(function(e) { 
                // prevent tap/click on filters panel to get to the body element
                e.stopPropagation(); 
            });

        $('#show-filters').click(function() {
            $('.wrapper-resources div.secondary')
                .animate({'margin-left': 0}, 300, function() {
                    $('body').on('click', hide_filters_on_body_click);
                });
        });

        //$('h3.filters-header .fa-close').click(function() {
        //    $('.wrapper-resources div.secondary').animate({'margin-left': '-350px'}, 300);
        //});
        $('h3 .fa-close').click(hide_filters_on_body_click);
    }
});
