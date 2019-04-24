from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

class PendingTimesheetReport(models.Model):
    _name = 'pending.timesheet.report'
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    project_id = fields.Many2one('project.project', string="Assignment")
    task_id = fields.Many2one('project.task', string="Task")
    manager_id = fields.Many2one('res.users', string="Manager")
    us_name_id = fields.Many2one('res.users', string="US Name")
    ea_name = fields.Many2one('res.users', string="EA Working")
    working_hour = fields.Float(string="Working Hours")
    timesheet_hour = fields.Float(string="Total Timesheet Hour")
    leave_hour = fields.Float(string="Leave Hours")
    pending_hour = fields.Float(string="Pending Hours")
    
    
    @api.multi
    def get_pending_timesheet_report(self):
        self.env['pending.timesheet.report'].search([]).unlink()
        line_ids = []
        timesheet_obj = self.env['account.analytic.line']
        domain = []
        project_ids = self.env['project.project'].search([])
        
        #find last week start and end date
        today = datetime.today().date()
        
        this_week_start_date = datetime.today() - timedelta(days=datetime.today().isoweekday() % 7)
        start_date = this_week_start_date- timedelta(days=7)
        end_date = this_week_start_date- timedelta(days=1)
        
        if start_date and end_date:
            domain = [('date', '>=', start_date), ('date', '<=', end_date),'|',('active', '=', True),('active', '=', False)]
            
        #need to make it task wise instead of client wise
        task_ids = timesheet_obj.search(domain)
        task_ids = task_ids.mapped('task_id')
        
        
        #Holiday Count Logic
#         holidays = self.env['public.holiday'].sudo().search([
#             ('public_holiday_date', '>=', start_date),
#             ('public_holiday_date', '<=', end_date)])
# 
#         holidays_count = len(holidays)
        
        for task in task_ids:
            
            #mapp with billing history
            domain_bill = [
                    ('invoice_end_date', '>=', end_date),
                    ('invoice_start_date', '!=', False),
                    ('invoice_end_date', '!=', False),
                    ('project_id', '=', task.project_id.id),
                    ]
            
            bill = self.env['billing.history'].sudo().search(domain_bill, limit=1)
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
            
#             holidays_hours = 0
#             if holidays_count > 0:
#                 daily_hours = float(min_hour) / 5
#                 holidays_hours = daily_hours * holidays_count
#              
#             min_hour -= holidays_hours
            
            
            timesheet_ids = timesheet_obj.search(domain + [('task_id', '=', task.id)])
            this_week_working_hour = 0
            for timesheet in timesheet_ids:
#                 if timesheet.type_of_view.billable:
                this_week_working_hour += timesheet.unit_amount
                    
            leave = self.env['project.leave'].sudo().search([
                            ('start_date', '>=', start_date),
                            ('end_date', '<=', end_date),
                            ('project_id', '=', task.project_id.id),
                            ('us_name_id', '=', task.project_id.jd_us_name_id.id),
                            ('state', '=', 'sent')])
            
            leave_hours = abs(sum(leave.mapped('leave_duration')))
            
#             if leave_hours >= 1.00:
#                 min_hour =  round((min_hour - leave_hours),2)
            pending_hours = min_hour - (leave_hours + this_week_working_hour)
            if pending_hours > 0:
                new_id = self.env['pending.timesheet.report'].create({
                                                            'start_date': start_date,
                                                            'end_date': end_date,
                                                            'project_id': task.project_id.id,
                                                            'task_id': task.id,
                                                            'manager_id': task.project_id.project_general_manager.id,
                                                            'us_name_id': task.project_id.jd_us_name_id.id,
                                                            'ea_name': task.project_id.jd_ea_working_id.id,
                                                            'working_hour': min_hour,
                                                            'timesheet_hour': this_week_working_hour,
                                                            'leave_hour': leave_hours,
                                                            'pending_hour' : pending_hours if pending_hours > 0 else 0
                                                            })
                line_ids.append(new_id.id)
        
                
        return {
            'name': 'Pending Timesheet Report',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_id': line_ids,
            'res_model': 'pending.timesheet.report',
            'view_id': self.env.ref('indimedi_crm.pending_timesheet_tree').id,
            'target': 'current',
            'context': {
            }
        }