from odoo import models, fields, api
import xlwt
import base64
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

    
class PeriodicReportWizard(models.TransientModel):
    _name = 'periodic.report.wizard'
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    file = fields.Binary('Timesheet Report', readonly=True)
    filename = fields.Char('Name', size=256)
    
        
    @api.multi
    def generate_report_xls(self):
        timesheet_obj = self.env['account.analytic.line']
        domain = []
        project_ids = self.env['project.project'].search([])
        if self.start_date and self.end_date:
            domain = [('date', '>=', self.start_date), 
                      ('date', '<=', self.end_date),
                      '|',('active', '=', True),
                      ('active', '=', False)]
            
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
            if task.project_id.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
                min_hour = (float(task.project_id.hour_selection) / 4)
            else:
                min_hour = float(task.project_id.hour_selection)
            
            holidays_hours = 0
            if holidays_count > 0:
                daily_hours = float(min_hour) / 5
                holidays_hours = daily_hours * holidays_count
             
            min_hour -= holidays_hours
#             
            related_employee_id = self.env['hr.employee'].search([('user_id', '=', task.user_id.id)])
            leaves = False
            if related_employee_id:
                leaves = self.env['hr.holidays'].search(
                    [('employee_id', '=', related_employee_id.id),
                    ('date_from', '>=', self.start_date),
                    ('date_to', '<=', self.end_date),
                    ('type', '=', 'remove')])
                
            leave_count = 0
            leave_hours = 0
            if leaves:
                leave_count = abs(sum(leaves.mapped('number_of_days')))
            
            
            if leave_count > 0:
                daily_hours = float(min_hour) / 5
                leave_hours = daily_hours * leave_count
             
            min_hour -= leave_hours
#           
            project_name = task.project_id.name
            
            min_hour_str = 0
            minutes = float(min_hour) * 60
            if minutes:
                min_hour_only, working_min = divmod(minutes, 60)
                min_hour_str = "%02d:%02d"%(min_hour_only, working_min)
            value = {
                    'client_name': task.client_reporting_id.name,
                    'manager_name': task.manager_id.name,
                    'gm_manager': task.project_id.project_general_manager.name,
                    'ea_working': task.user_id.name,
                    'us_name': task.jd_us_name_id.name,
                    'min_hour': min_hour_str or '00:00',
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
                   
            
            #this_week_working_hour in time formate
            working_hour = 0
            minutes = this_week_working_hour * 60
            if minutes:
                working_hour, working_min = divmod(minutes, 60)
                working_hour = "%02d:%02d"%(working_hour, working_min)
            
            
            
            value.update({
                        'this_week_working_hour': working_hour, 
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
        sheet.write(0, 7, 'Actual Hours Worked this week', format1)
        sheet.write(0, 8, 'Email', format1)
        sheet.write(0, 9, 'Chat',format1)
        sheet.write(0, 10, 'Phone', format1)
        
        sheet.col(0).width = int(30*350)
        sheet.col(1).width = int(30*260)
        sheet.col(2).width = int(30*220)
        sheet.col(3).width = int(30*220)
        sheet.col(4).width = int(30*220)
        sheet.col(5).width = int(30*220)
        sheet.col(6).width = int(30*280)
        sheet.col(7).width = int(30*260)
        sheet.col(8).width = int(30*260)
        sheet.col(9).width = int(30*260)
        sheet.col(10).width = int(30*260)
        
        
        
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
            sheet.write(row, col + 7, data['this_week_working_hour'])
            sheet.write(row, col + 11, data['email'])
            sheet.write(row, col + 12, data['chat'])
            sheet.write(row, col + 13, data['phone'])
            
            row += 1
        #create xls file
        filename = r'/tmp/Timesheet_Report.xls'
        workbook.save(filename)
        file = open(filename, "rb")
        file_data = file.read()
        out = base64.encodestring(file_data)
         
        self.write({'file': out, 'filename':'Timesheet Report.xls'})
         
        return {
           'type': 'ir.actions.act_window',
           'res_model': 'periodic.report.wizard',
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
        