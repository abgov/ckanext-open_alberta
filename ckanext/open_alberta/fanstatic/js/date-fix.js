$(function() {
    // replace HTML5 date inputs with JQuery UI if on a desktop as only Chrome and Opera support those
    if (!navigator.userAgent.match(/Mobi/)) {
        $('input[type=date]').each(function(idx) {
            $(this).prop('type', 'text')
                   .attr('placeholder','yyyy-mm-dd')
                   .datepicker({dateFormat: 'yy-mm-dd'});
        });
    }
});
