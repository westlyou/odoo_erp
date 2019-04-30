from odoo import models, fields, api
from odoo.exceptions import UserError
import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import collections
import xlwt
import base64


MONTH = ['January',
'February',
'March',
'April',
'May',
'June',
'July',
'August',
'September',
'October',
'November',
'December']

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
    file = fields.Binary('Forecast Report', readonly=True)
    filename = fields.Char('Name', size=256)
    
    @api.multi
    def get_forecast_report(self):
        workbook = xlwt.Workbook()  
        sheet = workbook.add_sheet("Forecast Report")
        
        vals = []
        forecast_data = {}#collections.OrderedDict()
        project_ids = self.env['project.project'].search([])
        
        for project_id in project_ids:
            print"project===========",project_id.name, project_id.date_of_join
            
            #get start and end Date
            real_start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
            real_end_date = real_start_date + relativedelta(days=-1, months=+self.forecast_month)
            
            
            start_date = False
            end_date = False
            if project_id.date_of_join > datetime.strftime(real_start_date, DEFAULT_SERVER_DATE_FORMAT):
                start_date = datetime.strptime(project_id.date_of_join, DEFAULT_SERVER_DATE_FORMAT)
            
            if project_id.invoice_end_date:    
                if project_id.invoice_end_date <= datetime.strftime(real_end_date, DEFAULT_SERVER_DATE_FORMAT):
                    end_date = datetime.strptime(project_id.invoice_end_date, DEFAULT_SERVER_DATE_FORMAT)
            
            if not start_date:
                start_date = real_start_date
            if not end_date:
                end_date = real_end_date
                
            #get working days
            
            days = end_date - start_date 
            
            print"start and end======================",start_date, end_date
                
            valid_date_list = {(start_date + timedelta(days=x)).strftime('%d-%b-%Y')
                                    for x in range(days.days + 1)
                                    if (start_date + timedelta(days=x)).isoweekday() <= 5
                                   }
            working_days = len(valid_date_list)
            #print"working_days===========",working_days
            
            #find min hour per day
            min_hour = 0
            if project_id.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
                min_hour = (float(project_id.hour_selection) / 4)
            if project_id.invoicing_type_id.name in ['Weekly', 'Weekly Advance']:
                min_hour = float(project_id.hour_selection)
                
            hour_per_day = 0
            if min_hour > 0:
                hour_per_day = float(min_hour) / 5
            
            min_hour_per_day = hour_per_day
            
            
            #mapp with billing history
            date_of_join = project_id.date_of_join
            #print"end_date===============",end_date
            
            domain = [
                    ('invoice_end_date', '>=', end_date),
                    ('invoice_start_date', '!=', False),
                    ('invoice_end_date', '!=', False),
                    ('project_id', '=', project_id.id),
                    ]
            
            bill = self.env['billing.history'].search(domain, limit=1)
            current_rate = 0
            hour_selection = 0
            if bill:
                current_rate = bill.rate_per_hour
                hour_selection = bill.hour_selection
            else:
                current_rate = project_id.rate_per_hour
                hour_selection = project_id.hour_selection
            
            #print"hour_selection=======",hour_selection,current_rate
            
#             month = self.forecast_month
#             month_start = start_date
#             
#             month_days = calendar.monthrange(start_date.year, start_date.month)[1]
#             #print"month_days============",month_days
#             month_end = month_start + relativedelta(days=month_days - start_date.day)
            #print"month end==============",month_end, month_start.month, month
            
            
#             for data in range(0, self.forecast_month):
#                 
#                 #logic of monthly forcast
#                 #
#                 #
#                 ########################
#                 print"month_start.month >= month_start.month=============",month_start.month ,month_start.month
#                 print("=================",month_start, month_end)
#                 month_start = month_start + relativedelta(months=+1)
#             
#                 month_days = calendar.monthrange(month_start.year, month_start.month)[1]
#                 
#                 month_end = month_start + relativedelta(days=month_days - month_start.day)
                    
                
            
            amount = working_days * min_hour_per_day * current_rate
            
            forecast_data.update({
                                'client_name': project_id.partner_id.name,
                                'project_name': project_id.name,
                                'gm_manager': project_id.project_general_manager.name,
                                'manager_name': project_id.user_id.name,
                                'amount': amount
                                })
            
        print"forecast_data\\\\\\\d",forecast_data
        format1 = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;') 
            
        sheet.write(0, 0, 'Client Name', format1)
        sheet.write(0, 1, 'Assignment', format1)
        sheet.write(0, 2, 'General manager', format1)
        sheet.write(0, 3, 'Project Manager', format1)
        sheet.write(0, 4, 'Amount', format1)        
        
        print"forecast_data===========",forecast_data   
        row = 1
        for data in forecast_data:
            col = 0
            sheet.write(row, col + 0, data['client_name'])
            sheet.write(row, col + 1, data['project_name'])
            sheet.write(row, col + 2, data['gm_manager'])
            sheet.write(row, col + 3, data['manager_name'])
            sheet.write(row, col + 4, data['amount'])        
             
            row += 1
                
        #create xls file
        filename = r'/tmp/Timesheet Forecast Report.xls'
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
         
        self.write({'file': out, 'filename':'Timesheet Forecast Report.xls'})
         
        return {
           'type': 'ir.actions.act_window',
           'res_model': 'invoice.forecast.wizard',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': self.id,
           'target': 'new',
        } 