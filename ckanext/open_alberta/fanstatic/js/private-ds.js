$(function() {
    $('#id-display-private-ds-only').on('change', function() {
        var me = $(this);
        window.location.href = me.is(':checked')? me.data('hrefPrivateDsOnly') : me.data('hrefAllDs');
    });
});
