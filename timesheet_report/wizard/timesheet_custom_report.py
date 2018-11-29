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
        
        timesheet_tds = False
        
        #{'client': [{'user': [{'ea_name': 'EA name', 'us_name': 'US name,'actual_work_hour': 30, 'productivity': 75%}]}]}
        
        timesheet_obj = self.env['account.analytic.line']
        
        doamin = []
        if self.start_date:
            doamin = [('date', '>=', self.start_date)]
        if self.end_date:
            doamin = [('date', '<=', self.end_date)]
            
        timesheet_tds = timesheet_obj.search(doamin, order='client_client_id')
        
        vals = {}
        for line in timesheet_tds:
            project_id = line.project_id
            task_id = line.task_id
            us_name = task_id.jd_us_name_id
            ea_working = project_id.jd_ea_working_id.name
            min_work = project_id.hour_selection
            manager_name = line.task_id.manager_id.name
            
            work_hour = 0
            if line.type_of_view.billable:
                work_hour = line.unit_amount
                    
            if not vals.get(line.client_client_id):
                vals[line.client_client_id] = [{us_name : [{'manager_name': manager_name,'ea_name': ea_working, 'actual_work_hour': work_hour, 'min_work': min_work}]}]
               
            else:
                client = vals.get(line.client_client_id)
                for user in client:
                    if user.get(us_name):
                        user_data = user[us_name][0]
                        if user_data:
                            timesheet_working = user_data.get('actual_work_hour') + work_hour
           
           
        workbook = xlwt.Workbook()  
        sheet = workbook.add_sheet("Timesheet")
        
        sheet.write(0, 0, 'Client name')
        sheet.write(0, 1, 'Manger Name')
        sheet.write(0, 2, 'Employee working (EA)')        
        sheet.write(0, 3, 'US Name')        
        sheet.write(0, 4, 'Minimum Hours Required to be worked')        
        sheet.write(0, 5, 'Actual Hours Worked (Without Training / Development)')
        sheet.write(0, 6, 'This week and Last week') 
        sheet.write(0, 7, 'Productivity to Minimum Bill')
        sheet.write(0, 8, 'Email')
        sheet.write(0, 9, 'Chat')
        sheet.write(0, 10, 'Phone')
        sheet.write(0, 11, 'Last Feedback Call')
#         sheet.write(0, 12, 'Last Feedback Call')
        
        row = 1   
        for client, data in vals.iteritems():
            col = 0
            #Client name
            sheet.write(row, col, client.name or '')
            for user, user_data in data[0].iteritems():
                ud = user_data[0]
                ea_name = ud.get('ea_name')
                manager_name = ud.get('manager_name')
                min_work = ud.get('min_work')
                actual_work_hour = ud.get('actual_work_hour')
                
                #Manger Name
                sheet.write(row, col+1, manager_name or '')
                
                #Employee working (EA)
                sheet.write(row, col+2, ea_name or '')
            
                #US Name
                us_name = task_id.jd_us_name_id.name
                sheet.write(row, col+3, user.name or '')
                
                #Minimum Hours Required to be worked
                sheet.write(row, col+4, min_work)
                
                #Actual Hours Worked (Without Training / Development
                sheet.write(row, col+5, actual_work_hour)
                
                #This week and Last week
                sheet.write(row, col+6, 'pending')
                
                #Productivity to Minimum Bill
                sheet.write(row, col+7, 'pending')
            
                #Email
                sheet.write(row, col+8, 'pending')
                
                #Chat
                sheet.write(row, col+9, 'pending')
                
                #Phone
                sheet.write(row, col+10, 'pending')
                
                
                #Last Feedback Call
                sheet.write(row, col+11, 'pending')
                
                
            row += 1
        
        filename = ('Timesheet Weekly Report'+ '.xls')
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
        
        self.write({'file': out, 'filename':'Timesheet Weekly Report.xls'})
        
        return {
           'type': 'ir.actions.act_window',
           'res_model': 'timesheet.report.wizard',
           'view_mode': 'form',
           'view_type': 'form',
           'res_id': self.id,
           'target': 'new',
        } 