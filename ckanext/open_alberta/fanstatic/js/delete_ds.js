$(function() {
    $('#id-delete-dss').on('change', function() {
        var me = $(this);
        delete_buttons = document.getElementsByName("delete-button");
        item_delete_checkboxs = $('[class*="lable-danger-item-delete"]');
        if (me.is(':checked')){
        	for (i = 0; i < delete_buttons.length; i++) {
        		delete_buttons[i].classList.remove('collapse');
        		delete_buttons[i].classList.add('collapse.in');
        	}
        	for (i = 0; i < item_delete_checkboxs.length; i++) {
        		item_delete_checkboxs[i].classList.remove('collapse');
        		item_delete_checkboxs[i].classList.add('collapse.in');
        	}
        }else{
        	for (i = 0; i < delete_buttons.length; i++) {
        		delete_buttons[i].classList.remove('collapse.in');
        		delete_buttons[i].classList.add('collapse');
        	}
        	for (i = 0; i < item_delete_checkboxs.length; i++) {
        		item_delete_checkboxs[i].classList.remove('collapse.in');
        		item_delete_checkboxs[i].classList.add('collapse');
        	}
        }
    });
	
	$(document).ready(function(){
        $('#id-delete-dss').prop('checked', false);
    });
});