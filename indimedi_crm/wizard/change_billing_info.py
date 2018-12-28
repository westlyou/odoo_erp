from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

#new file
class ChangeBillingInfo(models.Model):
    _name = 'change.billing.info'
    
    project_id = fields.Many2one('project.project', string="Project")
    invoice_start_date = fields.Date(string="Billing Start Date")
    rate_per_hour = fields.Float(string="Rate Per Hour", track_visibility='onchange')
    invoicing_type_id = fields.Many2one('job.invoicing', string="Invoicing Type", track_visibility='onchange')
    hour_selection = fields.Selection([('10','10 Hours'),('20','20 Hours'),('30','30 Hours'),
                                       ('40','40 Hours'),('80','80 Hours'),('90','90 Hours'),
                                       ('100','100 Hours'),('40_20','40-20 Hours'),
                                       ('20_10','20-10 Hours'),('160','160 Hours'),
                                       ('180','180 Hours'),('200','200 Hours')],
                                       string="Working Hours", track_visibility='onchange')
    total_rate = fields.Float(compute='_get_total_rate', string="Total Rate")
    
    
    @api.depends('hour_selection','rate_per_hour')
    def _get_total_rate(self):
        for rate in self:
            if rate.hour_selection == '40_20':
                rate.total_rate = round((float(rate.rate_per_hour)) * 60)
            elif rate.hour_selection == '20_10':
                rate.total_rate = round((float(rate.rate_per_hour)) * 30)
            elif rate.rate_per_hour and rate.hour_selection:
                rate.total_rate = round((float(rate.rate_per_hour)) * (float(rate.hour_selection)))
            else:
                pass

    
    @api.multi
    def action_update_billing_detail(self):
        vals = {'total_rate': self.total_rate}
        if self.rate_per_hour <= 0:
            raise UserError("Negative or zero rate is not allowed")
        