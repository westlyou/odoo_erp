from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class BillingHisory(models.Model):
    _name = 'billing.history'
    _order = 'invoice_start_date desc'
    
    project_id = fields.Many2one('project.project', string="Project")
    invoice_start_date = fields.Date(string="Billing Start Date")
    invoice_end_date = fields.Date(string="Billing End Date")
    rate_per_hour = fields.Float(string="Rate Per Hour", track_visibility='onchange')
    total_rate = fields.Float('Total Min. Rate', track_visibility='onchange')
    invoicing_type_id = fields.Many2one('job.invoicing', string="Invoicing Type", track_visibility='onchange')
    hour_selection = fields.Selection([('10','10 Hours'),('20','20 Hours'),('30','30 Hours'),
                                       ('40','40 Hours'),('80','80 Hours'),('90','90 Hours'),
                                       ('100','100 Hours'),('40_20','40-20 Hours'),
                                       ('20_10','20-10 Hours'),('160','160 Hours'),
                                       ('180','180 Hours'),('200','200 Hours')],
                                       string="Working Hours", track_visibility='onchange')
    user_id = fields.Many2one('res.users', string="Responsible")
    is_recent = fields.Boolean(string="Is Recent")


    @api.constrains('invoice_start_date', 'invoice_end_date')
    def _check_date(self):
        for history in self:
            domain = [
                ('invoice_start_date', '<=', history.invoice_end_date),
                ('invoice_end_date', '>=', history.invoice_start_date),
                ('id', '!=', history.id),
                ('project_id', '=', history.project_id.id)
                ]
            nhistory = self.search(domain)
            if nhistory:
                raise ValidationError(_('You can not have 2 billing that overlaps on the same day.'))
             
    @api.multi
    def open_update_billing_wizard(self):
        view_id = self.env.ref('indimedi_crm.change_billing_info_form')
        
        return {
                'name': "Update Billing Information",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'update.billing.line',
                'view_id': view_id.id,
                'target': 'new',
                'context': {'default_project_id': self.id},
        }
