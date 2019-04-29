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
        
        print"project===========",project_id.name, project_id.date_of_join
        
        #get start and end Date
        
        start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        end_date = start_date + relativedelta(months=+self.forecast_month)
        
#         last_day = calendar.monthrange(end_date.year,end_date.month)[1]
#         end_date = end_date.replace(day=last_day)
        
        
        #get billing info
            
        #mapp with billing history
        date_of_join = project_id.date_of_join
        print"date_of_join===============",end_date
        
        domain = [
                ('invoice_start_date', '>=', end_date),
                ('invoice_start_date', '!=', False),
                ('invoice_end_date', '!=', False),
                ('project_id', '=', project_id.id),
                ]
        
        bill = self.env['billing.history'].search(domain)
        current_rate = 0
        hour_selection = 0
        if bill:
            current_rate = bill[-1:].rate_per_hour
            hour_selection = bill[-1:].hour_selection
        else:
            current_rate = project_id.rate_per_hour
            hour_selection = project_id.hour_selection
        
        print"hour_selection=======",hour_selection,current_rate
            
        raise UserError("1")