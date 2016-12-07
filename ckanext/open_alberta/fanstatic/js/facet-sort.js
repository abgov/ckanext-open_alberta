$(function() {
    /*
     * Sort the search facets lists in "Refine Results" side bar
     */
    $('section.module h4 i.fa')
        .click(function() {
            var me = $(this);
            // find the sort class
            var clsParts = me.attr('class').split(/\s+/);
            for (var idx in clsParts) {
                var m = /^fa-sort-(amount|alpha)-(asc|desc)$/.exec(clsParts[idx]);
                if (m) {
                    var alphaSort = (m[1] == 'alpha');
                    var descending = (m[2] == 'desc');
                    var cls = m[0];
                    // Toggle sort icon and class
                    var newCls = 'fa-sort-' + m[1] + '-' + (descending? 'asc' : 'desc');
                    me.removeClass(cls).addClass(newCls);
                    // prepare sort table
                    var data2sort = [];
                    var ul = me.closest('section').find('>nav>ul:eq(0)');
                    ul.children().each(function(idx) { 
                        var txt = $(this).text().trim();
                        data2sort.push({
                            text: txt.replace(/\s\(\d+\)$/, ''),           // strip (<number>) from the end
                            amount: parseInt(txt.match(/\((\d+\))$/)[1]),  // extract the number
                            li: $(this)
                        });
                    });
                    var cmp;
                    if (alphaSort) {
                        if (descending) 
                            cmp = function(a,b) { return a.text<b.text? 1 : a.text>b.text? -1: 0; }
                        else
                            cmp = function(a,b) { return a.text>b.text? 1 : a.text<b.text? -1: 0; }
                    }
                    else {
                        if (descending) 
                            cmp = function(a,b) { return a.amount<b.amount? 1 : a.amount>b.amount? -1: 0; }
                        else
                            cmp = function(a,b) { return a.amount>b.amount? 1 : a.amount<b.amount? -1: 0; }
                    }
                    // remove li elements and re-insert in the proper order
                    ul.empty();
                    data2sort.sort(cmp).forEach(function(elem) {
                        ul.append(elem.li);
                    });
                    break;
                }
            }
        })
        .each(function() {
            // hide the sort icons if less then two elements in the list
            var me = $(this);
            if (me.closest('section').find('ul>li').length < 2)
                me.remove();
        });
});
