from odoo import models, fields, api
import xlwt
import base64
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


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
        project_ids = self.env['project.project'].search([])
        if self.start_date and self.end_date:
            domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date),'|',('active', '=', True),('active', '=', False)]
            
        #need to make it task wise instead of client wise
        task_ids = timesheet_obj.search(domain)
        task_ids = task_ids.mapped('task_id')
        
        
        #Holiday Count Logic
        holidays = self.env['public.holiday'].search([
            ('public_holiday_date', '>=', self.start_date),
            ('public_holiday_date', '<=', self.end_date)])

        holidays_count = len(holidays)
        
        vals = []
        for task in task_ids:
            
            #mapp with billing history
            domain_bill = [
                    ('invoice_end_date', '>=', self.end_date),
                    ('invoice_start_date', '!=', False),
                    ('invoice_end_date', '!=', False),
                    ('project_id', '=', task.project_id.id),
                    ]
            
            bill = self.env['billing.history'].search(domain_bill, limit=1)
            if bill:
                hour_selection = bill.hour_selection
            else:
                hour_selection = task.project_id.hour_selection
            if hour_selection == '40_20':
                hour_selection = 30
            if hour_selection == '20_10':
                hour_selection = 15
            
            if task.project_id.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
                min_hour = (float(hour_selection) / 4)
            else:
                min_hour = float(hour_selection)
            
            holidays_hours = 0
            if holidays_count > 0:
                daily_hours = float(min_hour) / 5
                holidays_hours = daily_hours * holidays_count
             
            min_hour -= holidays_hours
          
            leave = self.env['project.leave'].search([
                            ('start_date', '>=', self.start_date),
                            ('end_date', '<=', self.end_date),
                            ('project_id', '=', task.project_id.id),
                            ('us_name_id', '=', task.project_id.jd_us_name_id.id),
                            ('state', '=', 'sent')])
            
            leave_hours = abs(sum(leave.mapped('leave_duration')))
            
            if leave_hours >= 1.00:
                min_hour =  round((min_hour - leave_hours),2)
                        
            
                
            project_name = task.project_id.name
            
            min_hour_str = 0
            minutes = float(min_hour) * 60
            if minutes:
                min_hour_only, working_min = divmod(minutes, 60)
                min_hour_str = "%02d:%02d"%(min_hour_only, working_min)
            
            l_hour_str = ''
            if leave_hours:
                l_minutes = float(leave_hours) * 60
                l_hour_only, l_min = divmod(l_minutes, 60)
                l_hour_str = "%02d:%02d"%(l_hour_only, l_min)
            
            value = {
                    'client_name': task.client_reporting_id.name,
                    'manager_name': task.manager_id.name,
                    'gm_manager': task.project_id.project_general_manager.name,
                    'ea_working': task.user_id.name,
                    'us_name': task.jd_us_name_id.name,
                    'min_hour': min_hour_str or '00:00',
                    'leave_hours': l_hour_str,
                    'project_name': project_name,
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
        
            last_domain = [('date', '>=', last_start_date), ('date', '<=', last_end_date),('active', '=', False)]
            
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
                productivity_to_min_bill = (this_week_working_hour / float(min_hour)) * 100
            except:
                productivity_to_min_bill = 0
                
            
            
            #this_week_working_hour in time formate
            working_hour = 0
            minutes = this_week_working_hour * 60
            if minutes:
                working_hour, working_min = divmod(minutes, 60)
                working_hour = "%02d:%02d"%(working_hour, working_min)
            
            last_working_hour = 0
            minutes = last_week_working_hour * 60
            if minutes:
                last_working_hour, last_working_min = divmod(minutes, 60)
                last_working_hour = "%02d:%02d"%(last_working_hour, last_working_min)
            
            pructivity_against_last_week = round(pructivity_against_last_week, 2)
            pructivity_against_last_week_str = str(pructivity_against_last_week) + "%"
            
            productivity_to_min_bill = round(productivity_to_min_bill, 2)
            productivity_to_min_bill_str = str(productivity_to_min_bill) + "%"
            
            value.update({
                        'this_week_working_hour': working_hour, 
                        'last_week_working_hour': last_working_hour,
                        'pructivity_against_last_week': pructivity_against_last_week_str,
                        'productivity_to_min_bill': productivity_to_min_bill_str,
                        'email' : email,
                        'phone': phone,
                        'chat' : chat
                        })
            
            vals.append(value)
        
        workbook = xlwt.Workbook()  
        sheet = workbook.add_sheet("Timesheet")
         
        format1 = xlwt.easyxf('font:height 200,bold True;pattern: pattern solid, fore_colour gray25;') 
        
        sheet.write(0, 0, 'Project', format1)
        sheet.write(0, 1, 'Client name', format1)
        sheet.write(0, 2, 'Manger Name', format1)
        sheet.write(0, 3, 'General Manager', format1)
        sheet.write(0, 4, 'Employee working (EA)', format1)        
        sheet.write(0, 5, 'US Name', format1)        
        sheet.write(0, 6, 'Minimum Hours Required to be worked', format1)  
        sheet.write(0, 7, 'Leave Hours', format1)        
        sheet.write(0, 8, 'Actual Hours Worked this week', format1)
        sheet.write(0, 9, 'Actual Hours Worked last week', format1) 
        sheet.write(0, 10, 'Productivity against last week', format1)
        sheet.write(0, 11, 'Productivity to Minimum Bill', format1)
        sheet.write(0, 12, 'Email', format1)
        sheet.write(0, 13, 'Chat',format1)
        sheet.write(0, 14, 'Phone', format1)
#         sheet.write(0, 15, 'Last Feedback Call',format1)
        
        sheet.col(0).width = int(30*350)
        sheet.col(1).width = int(30*260)
        sheet.col(2).width = int(30*220)
        sheet.col(3).width = int(30*220)
        sheet.col(4).width = int(30*220)
        sheet.col(5).width = int(30*220)
        sheet.col(6).width = int(30*280)
        sheet.col(7).width = int(30*260)
        sheet.col(8).width = int(30*260)
        
        sheet.col(9).width = int(30*220)
        sheet.col(10).width = int(30*260)
        sheet.col(11).width = int(30*260)
        sheet.col(12).width = int(30*100)
        sheet.col(13).width = int(30*100)
        sheet.col(14).width = int(30*100)
        
        
        row = 1
        for data in vals:
            col = 0
            sheet.write(row, col + 0, data['project_name'])
            sheet.write(row, col + 1, data['client_name'])
            sheet.write(row, col + 2, data['manager_name'])
            sheet.write(row, col + 3, data['gm_manager'])
            sheet.write(row, col + 4, data['ea_working'])        
            sheet.write(row, col + 5, data['us_name'])        
            sheet.write(row, col + 6, data['min_hour']) 
            sheet.write(row, col + 7, data['leave_hours'])        
            sheet.write(row, col + 8, data['this_week_working_hour'])
            sheet.write(row, col + 9, data['last_week_working_hour']) 
            sheet.write(row, col + 10, data['pructivity_against_last_week'])
            sheet.write(row, col + 11, data['productivity_to_min_bill'])
            sheet.write(row, col + 12, data['email'])
            sheet.write(row, col + 13, data['chat'])
            sheet.write(row, col + 14, data['phone'])
#             sheet.write(row, col + 14, 'pending')
            
            row += 1
        #create xls file
        filename = r'/tmp/Timesheet_Weekly_Report.xls'
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
        elif count < 4  :
            return "Less Frequent"
        