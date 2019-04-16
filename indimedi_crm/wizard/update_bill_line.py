from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

#new file
class UpdateBillingLine(models.TransientModel):
    _name = 'update.billing.line'
    
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
    line = fields.Integer(string="Line")
    
    @api.multi
    def _validate_new_data(self):
        if self.rate_per_hour <= 0:
            raise UserError("Negative or zero rate is not allowed")
        if self.project_id.billing_history_ids:
            active_id = self._context.get('active_id')
            find_old_line = find_old_line = self.env['billing.history'].search([
                                                            ('project_id', '=', self.project_id.id),
                                                            ('id', '<', active_id)], limit=1)
            
            if find_old_line.invoice_start_date:
                if self.invoice_start_date <= find_old_line.invoice_start_date:
                    raise UserError("Invoice start date should greater then last start date %s"%(find_old_line.invoice_start_date))
        if not self.project_id.billing_history_ids:
            if self.invoice_start_date <= self.project_id.invoice_start_date:
                    raise UserError("Invoice start date should greater then last start date.")
                 
        if self.project_id.invoicing_type_id.name in ['Weekly', 'Weekly Advance']:
            date = fields.Datetime.from_string(self.invoice_start_date)
            if date.weekday() != 6:
                raise UserError("Start date should be on Sunday. for weekly invoice")
        if self.project_id.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
            date = fields.Datetime.from_string(self.invoice_start_date)
            if date.day != 1:
                raise UserError("Start date should be first date of month. for monthly invoice")
        
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
        self._validate_new_data()
        active_id = self._context.get('active_id')
        
        bill_id = self.env['billing.history'].browse(active_id)
        
        vals = {'total_rate': self.total_rate}
        
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
                        'rate_per_hour': bill_id.rate_per_hour
                        })
            
        if self.invoicing_type_id:
            vals.update({
                        'invoicing_type_id': self.invoicing_type_id.id
                        })
        else:
            vals.update({
                        'invoicing_type_id': bill_id.invoicing_type_id.id
                        })
        if self.hour_selection:        
            vals.update({
                        'hour_selection': self.hour_selection
                        })
        else:
            vals.update({
                        'hour_selection': bill_id.hour_selection
                        })

        
        find_old_line = self.env['billing.history'].search([('project_id', '=', self.project_id.id),
                                                            ('id', '>', active_id)])
        find_old_line.unlink()
        
        yesterday = datetime.strftime(fields.Datetime.from_string(self.invoice_start_date) - timedelta(1), DEFAULT_SERVER_DATE_FORMAT)
#         
#         find_old_line.invoice_end_date = yesterday
#          
        vals2 = {
                'project_id': self.project_id.id,
                'invoice_start_date': self.invoice_start_date,
                'invoice_end_date': False,
                'rate_per_hour': self.rate_per_hour,
                'total_rate': self.total_rate,
                'invoicing_type_id': self.invoicing_type_id.id or self.project_id.invoicing_type_id.id,
                'hour_selection': self.hour_selection,
                'user_id': self.env.user.id,
                } 
         
        self.project_id.write(vals)
        bill_id.write(vals2)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        
        
        