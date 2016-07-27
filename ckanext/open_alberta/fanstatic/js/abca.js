//Document-level functionality
$(document).ready(function(){
    prepareSideMenu();
    checkOpenTabs();
    checkDateRangePicker();
    formatDateValues();
});

$( window ).resize(function() {
    hideSideMenu();
});

function formatDateValues(){
    $('.format_as_date_simple').each(function(e){
        var h = $(this).html();
        h = h.split('T')[0];
        $(this).html(h);
    });
}

function checkDateRangePicker(){
    try{
        
        
        var urlvars = getUrlVars();
        var pickerVal = '';
        
        if(urlvars['q']){
            if(urlvars['q'].indexOf('metadata_created') >= 0){
                
                /*
                if($('input[name=daterangepicker_start]').val()){
                    pickerVal = $('input[name=daterangepicker_start]').val();
                }
                if($('input[name=daterangepicker_start]').val() && $('input[name=daterangepicker_end').val()){
                    pickerVal += ' to ';
                }
                if($('input[name=daterangepicker_end').val()){
                    pickerVal += $('input[name=daterangepicker_end').val();
                }
                */
                pickerVal = decodeURIComponent(urlvars['q']).replace('metadata_created:','').replace('TO',' to ').replace(']','').replace('[','').replace(/:/g,'').replace(/00/g,'').replace(/T/g,'').replace(/Z/g,'').replace(/\+/g,'');
                $('#daterange-publication').val(pickerVal.replace(/ [0-9]{2}:[0-9]{2}:[0-9]{2}/g,''));
                
                var resultText = $('.alberta-theme .module-content h2').html();
                resultText = resultText.split(':');
                $('.alberta-theme .module-content h2').html(resultText[0] + ': Date (' + pickerVal + ')');
            }
        }
        
    }catch(ex){
        
    }
}

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

function checkOpenTabs(){
    try{
        var url = document.location.toString();
        if (url.match('#')) {
            var tabname = url.split('#')[1];
            $('.tab-box').removeClass('active');
            $('.nav-tabs a[href=#'+tabname+']').tab('show');
            $('.tab-' + tabname).addClass('active');
        }

        $('.nav-tabs a').on('shown.bs.tab', function (e) {
            window.location.hash = e.target.hash;
        })
    }catch(ex){
           
    }
}

//Right hand side mobile menu functions
function prepareSideMenu(){
    $('body').click(function (e){
        if($('body').hasClass('pushed') && e.clientX < $('body').width() * 0.28){
            hideSideMenu();
        }
    });
}

function toggleSideMenu(){
    $('body').toggleClass('pushed');
    $('#quick-nav').toggleClass('open');
}

function hideSideMenu(){
    $('body').removeClass('pushed');
    $('#quick-nav').removeClass('open');
}

function openNavSub(navSection){
    $("#nav-local li").removeClass("active");
    $(".nav-sub-section").removeClass("opened");
    $('#nav-top-' + navSection).addClass("active");
    $('#nav-sub-' + navSection).addClass("opened");
}

function toggleFilters() {
    $('.left-sidebar').toggleClass('opened');
}
