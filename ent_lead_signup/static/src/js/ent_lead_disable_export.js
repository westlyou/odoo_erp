odoo.define('web.ent_lead_disable_export', function (require) {
"use strict";
    var Sidebar = require('web.Sidebar');
    var list_view = require('web.ListView');
    var core = require('web.core');
    var _t = core._t;
    var session = require('web.session');
    list_view.include({
        init : function(){
            this._super.apply(this, arguments);
        },
        render_sidebar: function($node) {
                if (!this.sidebar && this.options.sidebar) {
                        this.sidebar = new Sidebar(this, {editable: this.is_action_enabled('edit')});
                    if (this.fields_view.toolbar) {
                        this.sidebar.add_toolbar(this.fields_view.toolbar);
                    }
                    var other = []
                    if (this.model == 'crm.lead' && session.is_admin){
                        other.push({ label: _t("Export"), callback: this.on_sidebar_export })
                    }else if(this.model != 'crm.lead'){
                        other.push({ label: _t("Export"), callback: this.on_sidebar_export })
                    }
                    other.push([
                        this.fields_view.fields.active && {label: _t("Archive"), callback: this.do_archive_selected},
                        this.fields_view.fields.active && {label: _t("Unarchive"), callback: this.do_unarchive_selected},
                        this.is_action_enabled('delete') && { label: _t('Delete'), callback: this.do_delete_selected }])
                    this.sidebar.add_items('other', _.compact(other));

                    $node = $node || this.options.$sidebar;
                    this.sidebar.appendTo($node);

                    // Hide the sidebar by default (it will be shown as soon as a record is selected)
                    this.sidebar.do_hide();
                }
        },
    });
});
