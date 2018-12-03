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
        timesheet_obj = self.env['account.analytic.line']
        domain = []
        if self.start_date and self.end_date:
            domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]
            
        #need to make it task wise instead of client wise
        task_ids = timesheet_obj.search(domain)
        task_ids = task_ids.mapped('task_id')
        
        vals = []
        for task in task_ids:
            
            min_hour = task.project_id.hour_selection
            
            value = {
                    'client_name': task.client_reporting_id.name,
                    'manager_name': task.manager_id.name,
                    'ea_working': task.user_id.name,
                    'us_name': task.jd_us_name_id.name,
                    'min_hour': min_hour or 0,
                    }
            
            #find actual hour worked without training and dev. this week and last week
            email = 0
            phone = 0
            chat = 0
            
            timesheet_ids = timesheet_obj.search(domain + [('task_id', '=', task.id)])
            this_week_working_hour = 0
            for timesheet in timesheet_ids:
                
                if timesheet.comm_on_email:
                    email += 1
                if timesheet.comm_on_phone:
                    phone += 1
                if timesheet.comm_on_chat:
                    chat += 1
                
                    
                if timesheet.type_of_view.billable:
                    this_week_working_hour += timesheet.unit_amount
                    
            print"this_week_working_hour===================",this_week_working_hour        
            if chat:
                chat = self._check_communication_frequency(chat)
            else:
                chat = ''
            if phone:
                phone = self._check_communication_frequency(phone)
            else:
                phone = ''
            if email:
                email = self._check_communication_frequency(email)
            else:
                email = ''
                   
            #for last week
            last_start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
            last_start_date = last_start_date + timedelta(days=-7)
            last_end_date = last_start_date + timedelta(days=6)
            last_start_date = datetime.strftime(last_start_date, DEFAULT_SERVER_DATE_FORMAT)
            last_end_date = datetime.strftime(last_end_date, DEFAULT_SERVER_DATE_FORMAT)
        
            last_domain = [('date', '>=', last_start_date), ('date', '<=', last_end_date)]
            
            last_timesheet_ids = timesheet_obj.search(last_domain + [('task_id', '=', task.id)])
            
            last_week_working_hour = 0
            for timesheet in last_timesheet_ids:
                if timesheet.type_of_view.billable:
                    last_week_working_hour += timesheet.unit_amount
            
            try:
                pructivity_against_last_week = (this_week_working_hour / last_week_working_hour) * 100
            except:
                pructivity_against_last_week = 0
            
            try:
                productivity_to_min_bill = (this_week_working_hour / min_hour) * 100
            except:
                productivity_to_min_bill = 0
                
            
            value.update({
                        'this_week_working_hour': this_week_working_hour, 
                        'last_week_working_hour': last_week_working_hour,
                        'pructivity_against_last_week': pructivity_against_last_week,
                        'productivity_to_min_bill': productivity_to_min_bill,
                        'email' : email,
                        'phone': phone,
                        'chat' : chat
                        })
            
            vals.append(value)
        
        workbook = xlwt.Workbook()  
        sheet = workbook.add_sheet("Timesheet")
         
        sheet.write(0, 0, 'Client name')
        sheet.write(0, 1, 'Manger Name')
        sheet.write(0, 2, 'Employee working (EA)')        
        sheet.write(0, 3, 'US Name')        
        sheet.write(0, 4, 'Minimum Hours Required to be worked')        
        sheet.write(0, 5, 'Actual Hours Worked this week')
        sheet.write(0, 6, 'Actual Hours Worked last week') 
        sheet.write(0, 7, 'Productivity against last week')
        sheet.write(0, 8, 'Productivity to Minimum Bill')
        sheet.write(0, 9, 'Email')
        sheet.write(0, 10, 'Chat')
        sheet.write(0, 11, 'Phone')
        sheet.write(0, 12, 'Last Feedback Call')
        
        row = 1
        for data in vals:
            col = 0
            
            sheet.write(row, col + 0, data['client_name'])
            sheet.write(row, col + 1, data['manager_name'])
            sheet.write(row, col + 2, data['ea_working'])        
            sheet.write(row, col + 3, data['us_name'])        
            sheet.write(row, col + 4, data['min_hour'])        
            sheet.write(row, col + 5, data['this_week_working_hour'])
            sheet.write(row, col + 6, data['last_week_working_hour']) 
            sheet.write(row, col + 7, data['pructivity_against_last_week'])
            sheet.write(row, col + 8, data['productivity_to_min_bill'])
            sheet.write(row, col + 9, data['email'])
            sheet.write(row, col + 10, data['chat'])
            sheet.write(row, col + 11, data['phone'])
            sheet.write(row, col + 12, 'pending')
            
            row += 1
        #create xls file
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


    @api.multi
    def _check_communication_frequency(self, count=0):
        if count >= 5:
            return "Too Frequent"
        elif count == 4:
            return "Frequent"
        elif count < 4:
            return "Less Frequent"
        