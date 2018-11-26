odoo.define('indimedi_crm.widgets', function(require) {
"use strict";

var core = require('web.core');
var widgets = require('web_calendar.widgets');

var _t = core._t;
var QWeb = core.qweb;
	widgets.QuickCreate.include({
		init: function(parent, dataset, buttons, options, data_template) {
			this.dataset = dataset;
	        this._buttons = buttons || false;
	        this.options = options;
	        this.data_template = data_template || {};
			// this.data_template.name = "Meeting With " + dataset.context.default_name || '';
			this.data_template.name = dataset.context.default_name || '';
			return this._super(parent, dataset, buttons, options, data_template);
	   	}
   });
});