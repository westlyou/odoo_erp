from odoo import models, fields, api


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
    end_date = fields.Date(string="End Date")
    
    
    

    