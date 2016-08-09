
//Document-level functionality
$(document).ready(function(){
    activateTabs();
    loadDatasetNumbers();
    //var myURL = window.location.pathname.toLowerCase();
    //var dataset_type = $.QueryString['dataset_type'];
});

var countFP = 0;
var countDS = 0;
var countPN = 0;
var countOD = 0;
var targetFP = 0;
var targetOD = 0;
var targetDS = 0;
var targetPN = 0;
var delayOD = 0;
var delayFP = 0;
var delayDS = 0;
var delayPN = 0;

function loadDatasetNumbers(){
    try{
        
        if($('#query-count-documentation').length > 0 ||
           $('#query-count-publications').length > 0 ||
           $('#query-count-opendata').length > 0 ||
           $('#query-count-dataset').length > 0){
            setInterval(function(){
                if(delayFP > 0){
                    delayFP--;
                }else{
                    if(countFP <= targetFP){
                        if (targetFP==0){
                            $('#query-count-documentation h4').html('');
                        }else{
                            $('#query-count-documentation h4').html(addCommas(targetFP));
                        }
                        /*countFP += Math.max(1,Math.floor((targetFP - countFP)/1));*/
                    }
                }
                if(delayDS > 0){
                    delayDS--;
                }else{
                    if(countDS <= targetDS){
                        if (targetDS==0){
                            $('#query-count-dataset h4').html('');
                        }
                        else{
                            $('#query-count-dataset h4').html(addCommas(targetDS));
                        }
                        /*countDS += Math.max(1,Math.floor((targetDS - countDS)/10));*/
                    }
                }
                if(delayOD > 0){
                    delayOD--;
                }else{
                    if(countOD <= targetOD){
                        if (targetOD==0){
                             $('#query-count-opendata h4').html('');
                        }else{
                             $('#query-count-opendata h4').html(addCommas(targetOD));
                        }
                        /*countOD += Math.max(1,Math.floor((targetOD - countOD)/10));*/
                    }
                }
                if(delayPN > 0){
                    delayPN--;
                }else{
                    if(countPN <= targetPN){
                        if (targetPN==0){
                            $('#query-count-publications h4').html('');
                        }else{
                            $('#query-count-publications h4').html(addCommas(targetPN));
                        }
                        /*countPN += Math.max(1,Math.floor((targetPN - countPN)/10));*/
                    }
                }
            },5);
        }
        
        if($('#query-count-documentation').length > 0){
            $.ajax({url: '/api/3/action/package_search?q=type:documentation', success: function(q){
                delayFP = 10 + Math.floor(Math.random()*20);
                targetFP = q.result.count;
                /*
                if(targetFP == 0){
                    targetFP = Math.floor(Math.random() * 13000) + 20;
                }
                */
            }});
        }
        if($('#query-count-dataset').length > 0){
            $.ajax({url: '/api/3/action/package_search?q=type:dataset', success: function(q){
                delayDS = 10 + Math.floor(Math.random()*20);
                targetDS = q.result.count;
                /*
                if(targetDS == 0){
                    targetDS = Math.floor(Math.random() * 30000) + 20;
                }
                */
            }});
        }
        if($('#query-count-opendata').length > 0){
            $.ajax({url: '/api/3/action/package_search?q=type:opendata', success: function(q){
                delayOD = 10 + Math.floor(Math.random()*20);
                targetOD = q.result.count;
                /*
                if(targetOD == 0){
                    targetOD = Math.floor(Math.random() * 30000) + 20;
                }
                */
            }});
        }
        if($('#query-count-publications').length > 0){
            $.ajax({url: '/api/3/action/package_search?q=type:publications', success: function(q){
                delayPN = 10 + Math.floor(Math.random()*20);
                targetPN = q.result.count;
                /*
                if(targetPN == 0){
                    targetPN = Math.floor(Math.random() * 23000) + 20;
                }
                */
            }});
        }
    }catch(ex){
        if(console){
            console.log(ex.message);   
        }
    }
}

function activateTabs(){
    try
    {
        if($('ul.nav-tabs').length > 0){
            $('ul.nav-tabs li').click(function(e){
                var trg = e.target;
                $(trg).parent().siblings().removeClass('active');

                var group = $(trg).parent().attr('data-tab-group');
                var tab = $(trg).parent().attr('data-tab-name');
                $('[data-tab-group=' + group + ']').removeClass('active');
                $('.' + tab).addClass('active');
                $(trg).parent().addClass('active');
            });
        }
    }catch(ex){
        if(console){
            console.log(ex.message);
        }
    }

}

/*
function updateLinks(myURL,dataset_type){
        if(myURL.toLowerCase().indexOf("publications") > 0){
        $('h3.package-header a').each(function(i,e){
            $(e).attr('href', $(e).attr('href').replace('dataset','publications'));
        });
        try{
            $('a.btn-default').each(function(i,e){
                $(e).attr('href',$(e).attr('href').replace('/dataset','/publications'));
            });
        }catch(ex){
            console.log(ex.message);
        }
        try{
            if($('.search-form .col-xs-12 h2').html()){
                $('.search-form .col-xs-12 h2').html($('.search-form .col-xs-12 h2').html().replace('dataset','Publication'));
            }
        }catch(ex){
            console.log(ex.message);
        }
        try{
            $('.module .module-content .page_primary_action').html('<a class="btn btn-primary" href="/publications/new"><i class="icon-plus-sign-alt"></i> Add Publication</a>');
        }catch(ex){
            console.log(ex.message);
        }
    }
}
*/

function addCommas(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
    }
    return x1 + x2;
}
