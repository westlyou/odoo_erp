odoo.define('ent_lead_signup.lead_signup', function(require) {
"use strict";
	var base = require('web_editor.base');
    var core = require('web.core');
    var ajax = require('web.ajax');
    $(".signup_tc_pdf").hide()
	console.log("???????????????????//helloooo call aai gyo")
	console.log("?/////////////",$(".accept_tc_js"))
	$(".accept_tc_js").on("change",function(el){
		console.log(";;;;;;;;;;;;;;;;;;;;;;;;;;;",this.checked)
		if(this.checked){
			$(".signup_tc_pdf").show()
			$(".signup_submit").attr("disabled",false)
		}else{
			$(".signup_tc_pdf").hide()
			$(".signup_submit").attr("disabled",true)
		}
	});
});
