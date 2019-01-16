from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

#new file
class ChangeBillingInfo(models.TransientModel):
    _name = 'change.billing.info'
    
    project_id = fields.Many2one('project.project', string="Project")
    invoice_start_date = fields.Date(string="Billing Start Date")
    invoice_end_date = fields.Date(string="Billing End Date")
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
        if self.invoice_start_date:
            vals.update({
                        'invoice_start_date': self.invoice_start_date
                        })
        if self.rate_per_hour:
            vals.update({
                        'rate_per_hour': self.rate_per_hour
                        })
        else:
            vals.update({
                        'rate_per_hour': self.project_id.rate_per_hour
                        })
            
        if self.invoicing_type_id:
            vals.update({
                        'invoicing_type_id': self.invoicing_type_id.id
                        })
        else:
            vals.update({
                        'invoicing_type_id': self.project_id.invoicing_type_id.id
                        })
        if self.hour_selection:        
            vals.update({
                        'hour_selection': self.hour_selection
                        })
        else:
            vals.update({
                        'hour_selection': self.project_id.hour_selection
                        })
#             
#         vals.update({
#                 'project_id': self.project_id.id,
#                 })

        vals2 = {
                'project_id': self.project_id.id,
                'invoice_start_date': self.project_id.invoice_start_date,
                'invoice_end_date': self.invoice_end_date,
                'rate_per_hour': self.project_id.rate_per_hour,
                'total_rate': self.project_id.total_rate,
                'invoicing_type_id': self.project_id.invoicing_type_id.id,
                'hour_selection': self.project_id.hour_selection,
                'user_id': self.env.user.id,
                }
        
        self.project_id.write(vals)
        self.env['billing.history'].create(vals2)
        
        
        
        