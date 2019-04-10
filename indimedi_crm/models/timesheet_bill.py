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


class TimesheetInvoicePayment(models.Model):
    _name = "timesheet.invoice.payment"
    
    name = fields.Char(string="Name", default='Payment')
    amount = fields.Float(string="Payment Amount")
    date_payment = fields.Date(string="Payment Date")
    remark = fields.Text(string="Note")
    timesheet_invoice_ids = fields.One2many('timesheet.invoice', 'payment_id', string="Invoices")
    responsible_id = fields.Many2one('res.users', string="Responsible", readonly=True, default=lambda self: self.env.user)
    
class TimesheetInvoice(models.Model):
    _inherit = "timesheet.invoice"
    
    payment_id = fields.Many2one('timesheet.invoice.payment', string="Payment")
    