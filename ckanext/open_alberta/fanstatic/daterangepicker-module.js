this.ckan.module('daterangepicker-module', function($, _) {
    return {
        initialize: function() {
            // Add hidden <input> tags #start_date and #end_date,
            // if they don't already exist.
            var form = $(".search-form");

            $('input[id^="daterange"]').each(function() {
                var $item = $(this);
                
                
                if ($("#start_date").length === 0) {
                    $('<input type="hidden" id="' + $item.attr('data-field') + ' name="' + $item.attr('data-field') + '" />').appendTo(form);                
                }
                if ($("#" + $item.attr('data-field')).length === 0) {
                    $('<input type="hidden" id="' + $item.attr('data-field') + '" name="' + $item.attr('data-field') + '" />').appendTo(form);        
                }
                
            });

            // Add a date-range picker widget to the <input> with id thta starts with daterange
            $('input[id^="daterange"]').daterangepicker({
                ranges: {
                   'Today': [moment().startOf('day'), moment().endOf('day')],
                   'Yesterday': [moment().subtract('days', 1), moment().subtract('days', 1)],
                   'Last 7 Days': [moment().subtract('days', 6), moment()],
                   'Last 30 Days': [moment().subtract('days', 29), moment()],
                   'This Month': [moment().startOf('month'), moment().endOf('month')],
                   'Last Month': [moment().subtract('month', 1).startOf('month'), moment().subtract('month', 1).endOf('month')]
                },
                startDate: moment().subtract('days', 29),
                endDate: moment(),
                showDropdowns: true,
                timePicker: false
            },
            function(start, end) {
                var $this = $(this);
                // Bootstrap-daterangepicker calls this function after the user
                // picks a start and end date.

                // Format the start and end dates into strings in a date format
                // that Solr understands.
                start = start.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
                end = end.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
                var value = this.element.attr("data-field") + ":" +'[' + start + ' TO ' + end + ']';
                var form = $("#small_search");

                // Set the value of the hidden <input id="start_date"> to
                // the chosen start date.
                
                if ($("input[name=q]").length == 0) {
                    $('<input type="hidden" id="q" name="q" value="' + value  + '" />').appendTo(form);
                } else {
                    $("input[name=q]").val(value);
                }
                
                //$('#' + this.element.attr("data-field")).val();

                // Set the value of the hidden <input id="end_date"> to
                // the chosen end date.
                //$('#' + this.element.attr("data-field")).val(end);

                // Submit the <form id="dataset-search">.
                form.submit();
            });
        }
    }
});
