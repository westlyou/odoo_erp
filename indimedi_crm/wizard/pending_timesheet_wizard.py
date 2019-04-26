from odoo import models, fields, api
import xlwt
import base64
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class PendingTimesheetWizard(models.TransientModel):
    _name = 'pending.timesheet.wizard'
    
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(compute="_get_last_date", string="End Date")
    
    @api.depends('start_date')
    def _get_last_date(self):
        """let last day of week from start date date +7"""
        for data in self:
            if data.start_date:
                start_date = datetime.strptime(data.start_date, DEFAULT_SERVER_DATE_FORMAT)
                start_date = start_date + timedelta(days=6)
                data.end_date = start_date
                
                
    @api.multi
    def get_pending_timesheet_report(self):
        res = self.env['pending.timesheet.report'].get_pending_timesheet_report(start_date=self.start_date, end_date=self.end_date)
        return res