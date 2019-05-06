from odoo import models, fields, api
from odoo.exceptions import UserError
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class InvoiceForecastWizard(models.Model):
    _name = 'invoice.forecast.wizard'
    
    month = fields.Selection([(1, 'January'),
                              (2, 'February'),
                              (3, 'March'),
                              (4, 'April'),
                              (5, 'May'),
                              (6, 'June'),
                              (7, 'July'),
                              (8, 'August'),
                              (9, 'September'),
                              (10, 'October'),
                              (11, 'November'),
                              (12, 'December')], string="Start Month")
    start_date = fields.Date(string="Start Date")
    forecast_month = fields.Integer(string="Forecast Month")
    
    
    @api.multi
    def get_forecast_report(self):
        
        project_id = self.env['project.project'].search([('id','=',332)])
        
        print"project===========",project_id.name
        
        #get start and end Date
        today = datetime.now().date()
        
        start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        end_date = start_date + relativedelta(months=+self.forecast_month)
        
#         last_day = calendar.monthrange(end_date.year,end_date.month)[1]
#         end_date = end_date.replace(day=last_day)
        
        
        #get billing info
            
        #mapp with billing history
        
        while(start_date <= end_date):
            
            date = start_date
            
            
            domain_bill = [
                    ('invoice_end_date', '>=', end_date),
                    ('invoice_start_date', '!=', False),
                    ('invoice_end_date', '!=', False),
                    ('project_id', '=', project_id.id),
                    ]
            
            bill = self.env['billing.history'].sudo().search(domain_bill, limit=1)
            if bill:
                hour_selection = bill.hour_selection
                rate = project_id.rate_per_hour
            else:
                if project_id.date_of_joining >= start_date:
                    hour_selection = project_id.hour_selection
                    rate = project_id.rate_per_hour
                    
            print"bill========",start_date, hour_selection, rate
            
            
            print"dates=====================",start_date, end_date
            
            start_date = start_date + timedelta(days=1)        
        raise UserError("1")