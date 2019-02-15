# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import datetime
import time
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import dateutil.relativedelta
from odoo.exceptions import UserError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class TimesheetInvoice(models.Model):
    _name = "timesheet.invoice"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _order = 'invoice_start_date'

    project_id = fields.Many2one('project.project', string="Project")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Client Name',
        ondelete="cascade", required=True, auto_join=True)
    invoicing_type_id = fields.Many2one('job.invoicing', string="Invoicing Type")
    invoice_start_date = fields.Date(string="Start Date")
    invoice_end_date = fields.Date(string="End Date")
    hour_selection = fields.Selection([('10','10 Hours'),('20','20 Hours'),('30','30 Hours'),
                                       ('40','40 Hours'),('80','80 Hours'),('90','90 Hours'),
                                       ('100','100 Hours'),('40_20','40-20 Hours'),
                                       ('20_10','20-10 Hours'),('160','160 Hours'),
                                       ('180','180 Hours'),('200','200 Hours')],
                                       string="Working Hours")
    custom_work_hours = fields.Char(string="Working Hours")
    rate_per_hour = fields.Float(string="Rate Per Hour")
    min_bill = fields.Float('Min. Bill')
    worked_hours = fields.Float('Worked Hours')
    ideal_hours = fields.Float('Idle Hours')
    hours_charged = fields.Float(string='Hours Charged')
    bill_amount = fields.Float('Bill Amount')
    disc_amount = fields.Float('Disc. Amount')
    final_amount = fields.Float('Final Amount')
    holidays = fields.Float('Holidays', default=0.00)
    leave = fields.Float(string="Leave")
    billed = fields.Boolean(string="Billed")
    cancelled = fields.Boolean(string="Cancelled")
    sent_mail = fields.Boolean('Sent',default=False)
    invoice_date = fields.Date('Invoice Create Date', default=lambda self: fields.Datetime.now())
    additional_hours = fields.Float(string="Additional Hours")
    
    #new field added
    leave_days = fields.Float(string="Leave Days")
    leave_hours = fields.Float(string="Leave Hours")
    holidays_hours = fields.Float(string="Holiday Hour")
    hours_charged_save = fields.Float(string='Hours Charged Temp')
    is_paid = fields.Boolean(string="Paid")
    custom_work_hours_float = fields.Float(string="Working Hours Float")
    date_of_join = fields.Date(string="Date of Joining")
    
    @api.onchange('custom_work_hours', 'rate_per_hour')
    def onchange_custom_working_hour(self):
        custom_hour = float(self.custom_work_hours.split()[0])
        min_bill = custom_hour * self.rate_per_hour
        self.min_bill = min_bill
        
        self.hours_charged = (self.worked_hours + self.ideal_hours) if (self.worked_hours + self.ideal_hours) > custom_hour else custom_hour
        self.hours_charged_save = (self.worked_hours + self.ideal_hours) if (self.worked_hours + self.ideal_hours) > custom_hour else custom_hour
    
    @api.onchange('additional_hours')
    def onchange_additional_hours(self):
        hours_charged = self.hours_charged_save + self.additional_hours
        self.hours_charged = hours_charged
                
    @api.onchange('leave_hours', 'holidays')
    def onchange_leave_days(self):
        if self.invoicing_type_id.name in ['Weekly', 'Weekly Advance']:
            
            custom_work_hours = round(float(self.hour_selection),2)
            holidays_hours = 0
            leave_hours = 0
            if self.holidays > 0:
                daily_hours = float(self.hour_selection) / 5
                holidays_hours = daily_hours * self.holidays
                
                custom_work_hours =  round((float(self.hour_selection) - holidays_hours),2)
            else:
                custom_work_hours = custom_work_hours
                
            if self.leave_hours > 0:
                custom_work_hours =  round((float(custom_work_hours) - self.leave_hours),2)
    
            
            self.custom_work_hours = str(custom_work_hours) + " Hours"
            self.holidays_hours = holidays_hours
        if self.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
            start_date = datetime.datetime.strptime(self.invoice_start_date, DEFAULT_SERVER_DATE_FORMAT) 
            end_date =  datetime.datetime.strptime(self.invoice_end_date, DEFAULT_SERVER_DATE_FORMAT)
            
            
            days = end_date - start_date
            valid_date_list = {(start_date + datetime.timedelta(days=x)).strftime('%d-%b-%Y')
                                    for x in range(days.days+1)
                                    if (start_date + datetime.timedelta(days=x)).isoweekday() <= 5
                                   }
            working_days = len(valid_date_list)
            
            custom_work_hours = round(float(self.hour_selection),2)
            holidays_hours = 0
            leave_hours = 0
            if self.holidays > 0:
                daily_hours = float(self.hour_selection) / working_days
                holidays_hours = daily_hours * self.holidays
                
                custom_work_hours =  round((float(self.hour_selection) - holidays_hours),2)
            else:
                custom_work_hours = custom_work_hours
                
            if self.leave_hours > 0:
                custom_work_hours =  round((float(custom_work_hours) - leave_hours),2)
    
            self.custom_work_hours = str(custom_work_hours) + " Hours"
            self.holidays_hours = holidays_hours
    
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        if 'rate_per_hour' in fields:
            fields.remove('rate_per_hour')
        if 'min_bill' in fields:
            fields.remove('min_bill')
        return super(TimesheetInvoice, self).read_group(domain, fields, groupby, offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.onchange('hours_charged')
    def _onchange_bill_amount(self):
        self.bill_amount = self.hours_charged * self.rate_per_hour

    @api.onchange('bill_amount','disc_amount')
    def _onchange_final_amount(self):
        self.final_amount = self.bill_amount - self.disc_amount

    # @api.depends('worked_hours')
    # def _get_ideal_hours(self):
    #     if self.worked_hours < float(self.hour_selection):
    #         self.ideal_hours = float(self.hour_selection) - self.worked_hours

    @api.multi
    def send_timesheet_invoice(self):
        if not self.billed:
            raise UserError("You can only send invoice if its billed.")
        email = str(self.project_ids[0].client_email)
        ctx = dict(email_to=email)
        template = self.env.ref(
            'indimedi_crm.email_template_timesheet_sent')
        self.env['mail.template'].browse(
            template.id).with_context(ctx).send_mail(self.id,force_send=True)
        self.sent_mail = True


    @api.multi
    def mark_as_billed(self):
        if self.billed:
            raise UserError("The invoice is already Billed.")
        if self.cancelled:
            raise UserError("You can not mark cancelled invoice as billed.")
        self.billed = True

    @api.multi
    def mark_as_cancel(self):
        self.cancelled = True
        
    sequence_id = fields.Char('Invoice No.', index=True,readonly=True)

    @api.multi
    def mark_as_paid(self):
        if not self.billed:
            raise UserError("Only billed invoice can be paid!")
        self.is_paid = True
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('timesheet.invoice') or '/'
        vals['sequence_id'] = seq
        return super(TimesheetInvoice, self).create(vals)

    
#Schedular for Timesheet Invoice
class Project(models.Model):
    _inherit = 'project.project'

    def _PastweekBoundaries(self, year, week):
        startOfYear = date(year, 1, 1)
        week0 = startOfYear - timedelta(days=startOfYear.isoweekday())
        sun = week0 + timedelta(days = (week-2)*7)
        sat = sun + timedelta(days=6)
        return sun, sat
    # print weekBoundaries(int(dt.year), int(a))

    def _CurrentweekBoundaries(self, year, week):
        startOfYear = date(year, 1, 1)
        week0 = startOfYear - timedelta(days=startOfYear.isoweekday())
        sun = week0 + timedelta(days = (week-1)*7)
        sat = sun + timedelta(days=6)
        return sun, sat
    # print _CurrentweekBoundaries(int(dt.year), int(a))

    def _last_day_of_month(self, any_day):
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
        return next_month - datetime.timedelta(days=next_month.day)


    #This function is called when the weekly scheduler run
    @api.multi
    def weekly_invoice_scheduler_queue(self):
        project_obj = self.search([])
        for project in  project_obj:
            analytic_lines = self.env['account.analytic.account'].search([('project_ids', '=', project.id)])
            if analytic_lines:
                project_rec = analytic_lines.mapped('project_ids')
                if project_rec.invoicing_type_id.name == 'Weekly':
                    
                    is_last = False
                    for proj in project_rec:
                        is_last = False
                        dt = datetime.datetime.now()
                        a = datetime.date(int(dt.year), int(dt.month), int(dt.day)).isocalendar()[1]
                        b = int(dt.year)

                        date_in_between = self._PastweekBoundaries(int(b), int(a))
                        week_start = date_in_between[0]
                        week_end = date_in_between[1]
                        
                        #code for billing history by rate    
                        start_date = week_start.strftime(DF)
                        end_date = week_end.strftime(DF)
                        
                        #if project start date is future date then dont create invoice
                        if proj.dummy_start_date > start_date:
                            continue
                        
                        #if last invoice is created then dont create any more invoice
                        if proj.last_invoice_id:
                            continue
                        
                        #if end date is already passed then create last invoice
                        if proj.invoice_end_date and proj.invoice_end_date <= end_date:
                            print"=d========================",proj.invoice_end_date
                            is_last = True
                            
                        current_rate = 0
                        bill = False
                        
                        domain = [
                                ('invoice_end_date', '>=', end_date),
                                ('invoice_start_date', '!=', False),
                                ('invoice_end_date', '!=', False),
                                ('project_id', '=', proj.id),
                                ]
                        
                        bill = self.env['billing.history'].search(domain, limit=1)
                        
                        if bill:
                            current_rate = bill.rate_per_hour
                            hour_selection = bill.hour_selection
                        else:
                            current_rate = proj.rate_per_hour
                            hour_selection = proj.hour_selection
                        
                        #Holiday Count Logic
                        holidays = self.env['public.holiday'].search([
                            ('public_holiday_date', '>=', week_start.strftime(DF)),
                            ('public_holiday_date', '<=', week_end.strftime(DF))])

                        holidays_hours = 0
                        
                        if len(holidays) >= 1.00:
                            daily_hours = float(hour_selection) / 5
                            holidays_hours = daily_hours * len(holidays)
                            
                            custom_work_hours =  round((float(hour_selection) - holidays_hours),2)
                        else:
                            custom_work_hours = round(float(hour_selection),2)

                        domain = [('project_id', '=', proj.id), ('active', '=', False)]
                        if week_start and week_end:
                            domain.extend([('date', '>=', week_start.strftime(DF)), ('date', '<=', week_end.strftime(DF))])
                        timesheet_lines = self.env['account.analytic.line'].search(domain)
                        
                        
                        leave = self.env['project.leave'].search([
                            ('start_date', '>=', week_start.strftime(DF)),
                            ('end_date', '<=', week_end.strftime(DF)),
                            ('project_id', '=', proj.id),
                            ('us_name_id', '=', proj.jd_us_name_id.id),
                            ('state', '=', 'sent')])
                        
                        leave_hours = abs(sum(leave.mapped('leave_duration')))
                        
#                         leave_hours = 0
                        if leave_hours >= 1.00:
                            custom_work_hours =  round((float(custom_work_hours) - leave_hours),2)
                        
                        
                        worked_hour = 0
                        idel_hour = 0
                        break_hour = 0
                        
                        for line in timesheet_lines:
                            if line.type_of_view.billable:
                                worked_hour += line.unit_amount
                            elif line.type_of_view.idel:
                                idel_hour += line.unit_amount
                            elif line.type_of_view.is_break:
                                break_hour += line.unit_amount
                                
                        ideal_time = idel_hour
                        
                        if worked_hour > float(hour_selection):
                            extra_hours = worked_hour - float(hour_selection)
                        else:
                            extra_hours = 0.00
#                         

                        if worked_hour or ideal_time:
                            work_idle = worked_hour + ideal_time 
                            hour_charged = work_idle if work_idle > custom_work_hours else custom_work_hours
                            
                            invoice_lines = self.env['timesheet.invoice'].create({
                                    'project_id': proj.id,
                                    'analytic_account_id': proj.analytic_account_id.id,
                                    'invoicing_type_id': proj.invoicing_type_id.id,
                                    'invoice_start_date': week_start,
                                    'invoice_end_date': week_end,
                                    'hour_selection': hour_selection,
                                    'custom_work_hours': str(custom_work_hours) + str(' Hours'),
                                    'rate_per_hour': current_rate,
                                    'min_bill': custom_work_hours * current_rate,
                                    'worked_hours': worked_hour,
                                    'ideal_hours': ideal_time,
                                    'additional_hours': extra_hours,
                                    'hours_charged': hour_charged,
                                    'hours_charged_save': hour_charged,
                                    'bill_amount': hour_charged * current_rate,
                                    'final_amount': hour_charged * current_rate,
                                    'holidays': len(holidays),
                                    'leave_hours': leave_hours,
                                    'leave_days': 0,
                                    'holidays_hours': holidays_hours,
                                    'date_of_join': proj.date_of_join,
                                })
                        else:
                            work_idle = worked_hour + ideal_time 
                            hour_charged = work_idle if work_idle > custom_work_hours else custom_work_hours
                            invoice_lines = self.env['timesheet.invoice'].create({
                                    'project_id': proj.id,
                                    'analytic_account_id': proj.analytic_account_id.id,
                                    'invoicing_type_id': proj.invoicing_type_id.id,
                                    'invoice_start_date': week_start,
                                    'invoice_end_date': week_end,
                                    'hour_selection': hour_selection,
                                    'custom_work_hours': str(custom_work_hours) + str(' Hours'),
                                    'rate_per_hour': current_rate,
                                    'min_bill': custom_work_hours * current_rate,
                                    'worked_hours': worked_hour,
                                    'ideal_hours': ideal_time,
                                    'additional_hours': extra_hours,
                                    'hours_charged': hour_charged,
                                    'hours_charged_save': hour_charged,
                                    'bill_amount': hour_charged * current_rate,
                                    'final_amount': hour_charged * current_rate,
                                    'holidays': len(holidays),
                                    'leave_hours': leave_hours,
                                    'leave_days': 0,
                                    'holidays_hours': holidays_hours,
                                    'date_of_join': proj.date_of_join,
                                })
                        if is_last:
                            proj.last_invoice_id = invoice_lines.id
                        is_last = False

        return True


    #This function is called when the monthly scheduler run
    @api.multi
    def monthly_invoice_scheduler_queue(self):

        project_obj = self.search([])
        for project in  project_obj:
            analytic_lines = self.env['account.analytic.account'].search([('project_ids', '=', project.id)])
            if analytic_lines:
                project_rec = analytic_lines.mapped('project_ids')
                if project_rec.invoicing_type_id.name == 'Monthly':
                    is_last = False
                    for proj in project_rec:

                        # previous month logic
                        today = date.today()
                        d = today - relativedelta(months=1)
                        month_start = date(d.year, d.month, 1)
                        month_end = date(today.year, today.month, 1) - relativedelta(days=1)

                        # working Days count logic between months
                        start_date = month_start
                        end_date = month_end
                        days = end_date - start_date
                        valid_date_list = {(start_date + datetime.timedelta(days=x)).strftime('%d-%b-%Y')
                                                for x in range(days.days + 1)
                                                if (start_date + datetime.timedelta(days=x)).isoweekday() <= 5
                                               }
                        working_days = len(valid_date_list)
                    
                        # Holiday Count Logic
                        holidays = self.env['public.holiday'].search([
                            ('public_holiday_date', '>=', month_start.strftime(DF)),
                            ('public_holiday_date', '<=', month_end.strftime(DF))])
                        
                        # code for billing by rate    
                        start_date = month_start.strftime(DF)
                        end_date = month_end.strftime(DF)
                        
                        #if project start date is future date then dont create invoice
                        if proj.dummy_start_date > start_date:
                            continue
                        
                        #if last invoice is created then dont create any more invoice
                        if proj.last_invoice_id:
                            continue
                        
                        #if end date is already passed then create last invoice
                        if proj.invoice_end_date and proj.invoice_end_date <= end_date and not proj.last_invoice_id:
                            is_last = True
                        
                        
                        current_rate = 0
                        bill = False
                        
                        domain = [
                                ('invoice_end_date', '>=', end_date),
                                ('invoice_start_date', '!=', False),
                                ('invoice_end_date', '!=', False),
                                ('project_id', '=', proj.id),
                                ]
                        
                        bill = self.env['billing.history'].search(domain, limit=1)
                        if bill:
                            current_rate = bill.rate_per_hour
                            hour_selection = bill.hour_selection
                        else:
                            current_rate = proj.rate_per_hour
                            hour_selection = proj.hour_selection
                        
                        holidays_hours = 0
                        custom_work_hours = 0
                        if len(holidays) >= 1.00:
                            daily_hours = float(hour_selection) / working_days
                            holidays_hours = daily_hours * len(holidays)
                            custom_work_hours = round((float(hour_selection) - holidays_hours), 2)
                        else:
                            custom_work_hours = round(float(hour_selection), 2)

                        domain = [('project_id', '=', proj.id), ('active', '=', False)]
                        if month_start and month_end:
                            domain.extend([('date', '>=', month_start.strftime(DF)), ('date', '<=', month_end.strftime(DF))])
                        timesheet_lines = self.env['account.analytic.line'].search(domain)
                        
                        employee_ids = []
                        for line in timesheet_lines:
                            employee = self.env['hr.employee'].search([('user_id', '=', line.user_id.id)])
                            if employee:
                                employee_ids.append(employee.id)
                      
                        leave = self.env['project.leave'].search([
                            ('start_date', '>=', month_start.strftime(DF)),
                            ('end_date', '<=', month_end.strftime(DF)),
                            ('project_id', '=', proj.id),
                            ('us_name_id', '=', proj.jd_us_name_id.id),
                            ('state', '=', 'sent')])
                        
                        leave_hours = abs(sum(leave.mapped('leave_duration')))
                        if len(leave) >= 1.00:
                            custom_work_hours = round((float(custom_work_hours) - leave_hours), 2)
                            
                        
                        worked_hour, idel_hour, break_hour = 0, 0, 0
                        for line in timesheet_lines:
                            if line.type_of_view.billable:
                                worked_hour += line.unit_amount
                            elif line.type_of_view.idel:
                                idel_hour += line.unit_amount
                            elif line.type_of_view.is_break:
                                break_hour += line.unit_amount
                                
                        ideal_time = idel_hour
                        
                        if worked_hour > float(hour_selection):
                            extra_hours = worked_hour - float(hour_selection)
                        else:
                            extra_hours = 0.00
                            
                        if worked_hour or ideal_time:
                            
                            work_idle = worked_hour + ideal_time 
                            hour_charged = work_idle if work_idle > custom_work_hours else custom_work_hours
                            
                            invoice_lines = self.env['timesheet.invoice'].create({
                                    'project_id': proj.id,
                                    'analytic_account_id': proj.analytic_account_id.id,
                                    'invoicing_type_id': proj.invoicing_type_id.id,
                                    'invoice_start_date': month_start,
                                    'invoice_end_date': month_end,
                                    'hour_selection': hour_selection,
                                    # 'custom_work_hours': str(custom_work_hours) + str(' Hours'),
                                    'custom_work_hours':  str(custom_work_hours) + " Hours",  # proj.hour_selection + str(' Hours'),
                                    'rate_per_hour': current_rate,
                                    'min_bill': proj.total_rate,
                                    'worked_hours': worked_hour,
                                    'ideal_hours': ideal_time,
                                    'additional_hours': extra_hours,
                                    'hours_charged': hour_charged,
                                    'hours_charged_save': hour_charged,
                                    'bill_amount': hour_charged * current_rate,
                                    'final_amount': hour_charged * current_rate,
                                    'holidays': len(holidays),
                                    'holidays_hours': holidays_hours,
                                    'leave_days': 0,
                                    'leave_hours': leave_hours,
                                    'date_of_join': proj.date_of_join,
                                })
                        else:
                            work_idle = worked_hour + ideal_time 
                            hour_charged = work_idle if work_idle > custom_work_hours else custom_work_hours
                            invoice_lines = self.env['timesheet.invoice'].create({
                                    'project_id': proj.id,
                                    'analytic_account_id': proj.analytic_account_id.id,
                                    'invoicing_type_id': proj.invoicing_type_id.id,
                                    'invoice_start_date': month_start,
                                    'invoice_end_date': month_end,
                                    'hour_selection': hour_selection,
                                    # 'custom_work_hours': str(custom_work_hours) + str(' Hours'),
                                    'custom_work_hours':  str(custom_work_hours) + " Hours",  # proj.hour_selection + str(' Hours'),
                                    'rate_per_hour': current_rate,
                                    'min_bill': proj.total_rate,
                                    'worked_hours': worked_hour,
                                    'ideal_hours': ideal_time,
                                    'additional_hours': extra_hours,
                                    'hours_charged': hour_charged,
                                    'hours_charged_save': hour_charged,
                                    'bill_amount': hour_charged * current_rate,
                                    'final_amount': hour_charged * current_rate,
                                    'holidays': len(holidays),
                                    'holidays_hours': holidays_hours,
                                    'leave_days': 0,
                                    'leave_hours': leave_hours,
                                    'date_of_join': proj.date_of_join,
                                })
                        if is_last:
                            proj.last_invoice_id = invoice_lines.id
                        is_last = False

        return True

    #This function is called when the MONTHLY ADVANCE scheduler run
    @api.multi
    def monthly_advance_invoice_scheduler_queue(self):

        def last_day_of_next_month(date):
            if date.month == 12:
                return date.replace(day=31)
            return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

        project_obj = self.search([])
        for project in  project_obj:
            analytic_lines = self.env['account.analytic.account'].search([('project_ids', '=', project.id)])
            if analytic_lines:
                project_rec = analytic_lines.mapped('project_ids')
                is_last = False
                if project_rec.invoicing_type_id.name == 'Monthly Advance':
                    for proj in project_rec:

                        #next month date logic
                        today1 = date.today()
                        d1 = today1 + relativedelta(months=1)
                        start_date = datetime.date(d1.year, d1.month, 1)
                        end_date = last_day_of_next_month(start_date)#datetime.date(date.year, date.month, calendar.mdays[date.month])


                        #previous month logic
                        today2 = date.today()
                        d2 = today2 - relativedelta(months=1)
                        date11 = date(d2.year, d2.month, 1)
                        date22 = date(today2.year, today2.month, 1) - relativedelta(days=1)


                        #This month logic
                        dt = datetime.datetime.now()
                        a = datetime.date(int(dt.year), int(dt.month), int(dt.day)).isocalendar()[1]
                        b = int(dt.year)
                        c = int(dt.month)
                        month_start = datetime.date(int(dt.year), int(dt.month), 1)
                        month_end = self._last_day_of_month(datetime.date(int(dt.year), int(dt.month), int(dt.day)))


                        #Holiday Count Logic
                        holidays = self.env['public.holiday'].search([
                            ('public_holiday_date', '>=', month_start.strftime(DF)),
                            ('public_holiday_date', '<=', month_end.strftime(DF))])
                        
                        # end

                        #WORKING DAYS LOGIC
                        start_date = month_start
                        end_date = month_end
                        days = end_date - start_date
                        valid_date_list = {(start_date + datetime.timedelta(days=x)).strftime('%d-%b-%Y')
                                                for x in range(days.days+1)
                                                if (start_date + datetime.timedelta(days=x)).isoweekday() <= 5
                                               }
                        working_days = len(valid_date_list)


                        #code for billing by rate    
                        start_date = month_start.strftime(DF)
                        end_date = month_end.strftime(DF)
                        
                        #if project start date is future date then dont create invoice
                        if proj.dummy_start_date > start_date:
                            continue
                        
                        #if last invoice is created then dont create any more invoice
                        if proj.last_invoice_id:
                            continue
                        
                        #if end date is already passed then create last invoice
                        if proj.invoice_end_date and proj.invoice_end_date <= end_date and not proj.last_invoice_id:
                            is_last = True
                        
                        
                        current_rate = 0
                        bill = False
                        
                        domain = [
                                ('invoice_end_date', '>=', end_date),
                                ('invoice_start_date', '!=', False),
                                ('invoice_end_date', '!=', False),
                                ('project_id', '=', proj.id),
                                ]
                        
                        bill = self.env['billing.history'].search(domain,limit=1)
                        if bill:
                            current_rate = bill.rate_per_hour
                            hour_selection = bill.hour_selection
                            
                        else:
                            current_rate = proj.rate_per_hour
                            hour_selection = proj.hour_selection
                               
                               
                               
                        holidays_hours = 0
                        if len(holidays) >= 1.00:
                            daily_hours = float(hour_selection) / working_days
                            holidays_hours = daily_hours * len(holidays)
                            custom_work_hours = round((float(hour_selection) - holidays_hours),2)
                        else:
                            custom_work_hours = round(float(hour_selection),2)
                        
                        
                        domain = [('project_id', '=', proj.id), ('active', '=', False)]
                        if month_start and month_end:
                            domain.extend([('date', '>=', date11.strftime(DF)), ('date', '<=', date22.strftime(DF))])
                        timesheet_lines = self.env['account.analytic.line'].search(domain)
                        
                        
                        leave = self.env['project.leave'].search([
                            ('start_date', '>=', month_start.strftime(DF)),
                            ('end_date', '<=', month_end.strftime(DF)),
                            ('project_id', '=', proj.id),
                            ('us_name_id', '=', proj.jd_us_name_id.id),
                            ('state', '=', 'sent')])
                        
                        leave_hours = abs(sum(leave.mapped('leave_duration')))
                        
                        if leave_hours > 1.00:
                            custom_work_hours =  round((float(custom_work_hours) - leave_hours),2)
                         
                         
                        
                        
                        worked_hour,idel_hour,break_hour = 0,0,0
                        for line in timesheet_lines:
                            if line.type_of_view.billable:
                                worked_hour += line.unit_amount
                            elif line.type_of_view.idel:
                                idel_hour += line.unit_amount
                            elif line.type_of_view.is_break:
                                break_hour += line.unit_amount
                                
                        ideal_time = idel_hour
                        
                        if worked_hour > float(hour_selection):
                            extra_hours = worked_hour - float(hour_selection)
                        else:
                            extra_hours = 0.00

                        total_charged = float(hour_selection) + extra_hours

                        invoice_lines = self.env['timesheet.invoice'].create({
                                'project_id': proj.id,
                                'analytic_account_id': proj.analytic_account_id.id,
                                'invoicing_type_id': proj.invoicing_type_id.id,
                                'invoice_start_date': month_start,
                                'invoice_end_date': month_end,
                                'hour_selection': hour_selection,
                                # 'custom_work_hours': str(custom_work_hours) + str(' Hours'),
                                'custom_work_hours':  str(custom_work_hours) + " Hours", #proj.hour_selection + str(' Hours'),
                                'rate_per_hour': current_rate,
                                'min_bill': proj.total_rate,
                                'worked_hours': worked_hour,#float(proj.hour_selection),
                                'ideal_hours': ideal_time,
                                'additional_hours': extra_hours,
                                'hours_charged': total_charged,
                                'hours_charged_save': total_charged,
                                'bill_amount': total_charged * current_rate,
                                'final_amount': total_charged * current_rate,
                                'holidays': len(holidays),
                                'holidays_hours': holidays_hours,
                                'leave_days': 0,
                                'leave_hours': leave_hours,
                                'date_of_join': proj.date_of_join,
                            })
                        if is_last:
                            proj.last_invoice_id = invoice_lines.id
                        is_last = False

        return True


    #This function is called when the weekly Advance scheduler run
    @api.multi
    def weekly_advance_invoice_scheduler_queue(self):

        project_obj = self.search([])
        for project in  project_obj:
            analytic_lines = self.env['account.analytic.account'].search([('project_ids', '=', project.id)])
            if analytic_lines:
                project_rec = analytic_lines.mapped('project_ids')
                is_last = False
                if project_rec.invoicing_type_id.name == 'Weekly Advance':
                    for proj in project_rec:

                        #Previous Week DateRange Logic
                        prev_dates = []
                        today = date.today()
                        prev_monday = today - datetime.timedelta(days=today.weekday(), weeks=1)
                        prev_sunday = prev_monday - datetime.timedelta(days=1)
                        prev_saturday = prev_monday + datetime.timedelta(days=5)


                        #Current Week DateRange Logic
                        dt = datetime.datetime.now()
                        a = datetime.date(int(dt.year), int(dt.month), int(dt.day)).isocalendar()[1]
                        b = int(dt.year)

                        date_in_between = self._CurrentweekBoundaries(int(b), int(a))
                        week_start = date_in_between[0]
                        week_end = date_in_between[1]

                        #Holiday Count Logic
                        holidays = self.env['public.holiday'].search([
                            ('public_holiday_date', '>=', week_start.strftime(DF)),
                            ('public_holiday_date', '<=', week_end.strftime(DF))])

                        #code for billing by rate    
                        start_date = week_start.strftime(DF)
                        end_date = week_end.strftime(DF)
                        
                        #if project start date is future date then dont create invoice
                        if proj.dummy_start_date > start_date:
                            continue
                        
                        #if last invoice is created then dont create any more invoice
                        if proj.last_invoice_id:
                            continue
                        
                        #if end date is already passed then create last invoice
                        if proj.invoice_end_date and proj.invoice_end_date <= end_date and not proj.last_invoice_id:
                            is_last = True
                        
                        
                        current_rate = 0
                        bill = False
                        
                        domain = [
                                ('invoice_end_date', '>=', end_date),
                                ('invoice_start_date', '!=', False),
                                ('invoice_end_date', '!=', False),
                                ('project_id', '=', proj.id),
                                ]
                        
                        bill = self.env['billing.history'].search(domain,limit=1)
                        if bill:
                            current_rate = bill.rate_per_hour
                            hour_selection = bill.hour_selection
                        else:
                            current_rate = proj.rate_per_hour
                            hour_selection = proj.hour_selection
                               
                               
                        holidays_hours = 0
                        if len(holidays) >= 1.00:
                            daily_hours = float(hour_selection) / 5
                            holidays_hours = daily_hours * len(holidays)
                            custom_work_hours = round((float(hour_selection) - holidays_hours),2)
                        else:
                            custom_work_hours = round(float(hour_selection),2)


                        domain = [('project_id', '=', proj.id), ('active', '=', False)]
                        if prev_sunday and prev_saturday:
                            domain.extend([('date', '>=', prev_sunday.strftime(DF)), ('date', '<=', prev_saturday.strftime(DF))])
                        timesheet_lines = self.env['account.analytic.line'].search(domain)

                        employee_ids = []
                        for line in timesheet_lines:
                            employee = self.env['hr.employee'].search([('user_id','=', line.user_id.id)])
                            if employee:
                                employee_ids.append(employee.id)
                        
                        leave = self.env['project.leave'].search([
                            ('start_date', '>=', week_start.strftime(DF)),
                            ('end_date', '<=', week_end.strftime(DF)),
                            ('project_id', '=', proj.id),
                            ('us_name_id', '=', proj.jd_us_name_id.id),
                            ('state', '=', 'sent')])
                        
                        leave_hours = abs(sum(leave.mapped('leave_duration')))
                        
                        if leave_hours > 1.00:
                            custom_work_hours =  round((float(custom_work_hours) - leave_hours),2)
                          
                        worked_hour = 0
                        idel_hour = 0
                        break_hour = 0
                        for line in timesheet_lines:
                            if line.type_of_view.billable:
                                worked_hour += line.unit_amount
                            elif line.type_of_view.idel:
                                idel_hour += line.unit_amount
                            elif line.type_of_view.is_break:
                                break_hour += line.unit_amount
                                
                        ideal_time = idel_hour
                        
                        if worked_hour > float(hour_selection):
                            extra_hours = worked_hour - float(hour_selection)
                        else:
                            extra_hours = 0.00


                        total_charged = custom_work_hours + extra_hours

                        invoice_lines = self.env['timesheet.invoice'].create({
                                'project_id': proj.id,
                                'analytic_account_id': proj.analytic_account_id.id,
                                'invoicing_type_id': proj.invoicing_type_id.id,
                                'invoice_start_date': week_start,
                                'invoice_end_date': week_end,
                                'hour_selection': hour_selection,
                                'custom_work_hours':  str(custom_work_hours) + " Hours", #proj.hour_selection + str(' Hours'),
                                'rate_per_hour': current_rate,
                                'min_bill': custom_work_hours * current_rate,
                                # 'worked_hours': float(proj.hour_selection),
                                'worked_hours': worked_hour,
                                'ideal_hours': ideal_time,
                                'additional_hours': extra_hours,
                                # 'hours_charged': sum_hours if sum_hours > custom_work_hours else custom_work_hours,
                                # 'bill_amount': (sum_hours if sum_hours > custom_work_hours else custom_work_hours) * proj.rate_per_hour,
                                # 'final_amount': (sum_hours if sum_hours > custom_work_hours else custom_work_hours) * proj.rate_per_hour,
                                'hours_charged': total_charged,
                                'hours_charged_save': total_charged,
                                'bill_amount': total_charged * current_rate,
                                'final_amount': total_charged * current_rate,
                                'holidays': len(holidays),
                                'holidays_hours': holidays_hours,
                                'leave_days': 0,
                                'leave_hours': leave_hours,
                                'date_of_join': proj.date_of_join,
                            })
                        if is_last:
                            proj.last_invoice_id = invoice_lines.id

        return True
