odoo.define('ent_lead_signup.lead_signup', function(require) {
"use strict";
	var base = require('web_editor.base');
    var core = require('web.core');
    var ajax = require('web.ajax');
    $(".signup_tc_pdf").hide()

	if ($("input[name='hiring_perm']:checked").length > 0){
			$(".perm_input").show()
	}else{
		$(".perm_input").each(function(el){
			$(this).val("")
		})
		$(".perm_input").hide()
	}

	if ($("input[name='hiring_model_temporary']:checked").length > 0){
		$(".tempor_input").show()
	}else{
		$(".tempor_input").each(function(el){
			$(this).val("")
		})
		$(".tempor_input").hide()
	}
	
	if($("input[name='hiring_model_ondemand']:checked").length > 0){
		$(".ondemand_input").show()
	}else{
		$(".ondemand_input").each(function(el){
			$(this).val("")
		})
		$(".ondemand_input").hide()
	}
	
	
	$(".accept_tc_js").on("change",function(el){
		if(this.checked){
			$(".signup_tc_pdf").show()
			$(".signup_submit").attr("disabled",false)
		}else{
			$(".signup_tc_pdf").hide()
			$(".signup_submit").attr("disabled",true)
		}
	});
	
	$("input[name='hiring_perm']").on("change", function(ev){
		if (this.checked){
			$(".perm_input").show()
			$("input[name='hiring_model_temporary']").prop("checked", false)
			$("input[name='hiring_model_ondemand']").prop("checked", false)
			
			$("input[name='hiring_model_temporary']").trigger("change")
			$("input[name='hiring_model_ondemand']").trigger("change")
		}else{
			$(".perm_input").each(function(el){
				$(this).val("")
			})
			$(".perm_input").hide()
		}
	});
	
	$("input[name='hiring_model_temporary']").on("change", function(ev){
		if (this.checked){
			$(".tempor_input").show()

			$("input[name='hiring_perm']").prop("checked", false)
			$("input[name='hiring_model_ondemand']").prop("checked", false)

			$("input[name='hiring_perm']").trigger("change")
			$("input[name='hiring_model_ondemand']").trigger("change")
		}else{
			$(".tempor_input").each(function(el){
				$(this).val("")
			})
			$(".tempor_input").hide()
		}
	});
	
	$("input[name='hiring_model_ondemand']").on("change", function(ev){
		if (this.checked){
			$(".ondemand_input").show()
			$("input[name='hiring_model_temporary']").prop("checked", false)
			$("input[name='hiring_perm']").prop("checked", false)
			
			$("input[name='hiring_model_temporary']").trigger("change")
			$("input[name='hiring_perm']").trigger("change")
		}else{
			$(".ondemand_input").each(function(el){
				$(this).val("")
			})
			$(".ondemand_input").hide()
		}
	});
	
	$("select[name='s_tax_id_ids']").on("change", function(el){
		var opts = [], opt, str_opt='';
		var sel = this
		for (var i=0, len=sel.options.length; i<len; i++) {
		    opt = sel.options[i];
		    
		    if ( opt.selected ) {
	        	if (opt.value != ''){
	        		str_opt += opt.value + ', ';
	        	}
		    }
		}
		var option_str = str_opt.slice(0, -2);
		$("textarea[name='s_tax_id_id']").html(option_str)
	});
	
});