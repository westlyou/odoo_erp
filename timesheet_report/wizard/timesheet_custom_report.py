from odoo import models, fields, api
import xlwt
import base64
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TimesheetCustomReport(models.TransientModel):
    _name = 'timesheet.custom.report'
    
    client_id = fields.Char(string="Client Name")
    manager_id = fields.Char(string="Manager")
    employee_working = fields.Char(string="Employee Working")
    us_name = fields.Char(string="US Name")
    min_hour = fields.Char(string="Minimum Hour")
    actual_hour = fields.Float(string="Actual Hour")
    actual_hour_lst_week = fields.Float(string="Actual Hour/Last Week")
    productivity_against_last_Week = fields.Float(string="Productivity Against Last week")
    productivity_to_min_bill = fields.Float(string="Productivity to Minimum Bill")
    
    
class TimesheetReportWizard(models.TransientModel):
    _name = 'timesheet.report.wizard'
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(compute="_get_last_date", string="End Date")
    file = fields.Binary('Timesheet Report', readonly=True)
    filename = fields.Char('Name', size=256)
    
    @api.depends('start_date')
    def _get_last_date(self):
        """let last day of week from start date date +7"""
        for data in self:
            if data.start_date:
                start_date = datetime.strptime(data.start_date, DEFAULT_SERVER_DATE_FORMAT)
                start_date = start_date + timedelta(days=6)
                data.end_date = start_date 
        
    @api.multi
    def generate_report_xls(self):
        
        doamin = []
        if self.start_date:
            doamin = [('date', '>=', self.start_date)]
        if self.end_date:
            doamin = [('date', '<=', self.end_date)]
            
        #need to make it task wise instead of client wise
        project_ids = self.env['project.task'].search(doamin)
        
#         workbook = xlwt.Workbook()  
#         sheet = workbook.add_sheet("Timesheet")
#         
#         sheet.write(0, 0, 'Client name')
#         sheet.write(0, 1, 'Manger Name')
#         sheet.write(0, 2, 'Employee working (EA)')        
#         sheet.write(0, 3, 'US Name')        
#         sheet.write(0, 4, 'Minimum Hours Required to be worked')        
#         sheet.write(0, 5, 'Actual Hours Worked (Without Training / Development)')
#         sheet.write(0, 6, 'This week and Last week') 
#         sheet.write(0, 7, 'Productivity to Minimum Bill')
#         sheet.write(0, 8, 'Email')
#         sheet.write(0, 9, 'Chat')
#         sheet.write(0, 10, 'Phone')
#         sheet.write(0, 11, 'Last Feedback Call')
# #         sheet.write(0, 12, 'Last Feedback Call')
#         
#         
#         filename = ('Timesheet Weekly Report'+ '.xls')
#         workbook.save(filename)
#         file = open(filename, "rb")
#         file_data = file.read()
#         out = base64.encodestring(file_data)
#         
#         self.write({'file': out, 'filename':'Timesheet Weekly Report.xls'})
#         
#         return {
#            'type': 'ir.actions.act_window',
#            'res_model': 'timesheet.report.wizard',
#            'view_mode': 'form',
#            'view_type': 'form',
#            'res_id': self.id,
#            'target': 'new',
#         } 