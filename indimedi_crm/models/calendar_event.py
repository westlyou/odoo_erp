# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta

import time


class Meeting(models.Model):
    _inherit = 'calendar.event'

    stop_datetime = fields.Datetime('Stop Datetime',store=True)
    crm_id = fields.Many2one('crm.lead')
    meeting_status = fields.Text('Meeting Status / Feedback', states={'done': [('readonly', True)]})
    cal_street = fields.Char('Street')
    cal_street2 = fields.Char('Street2')
    cal_street3 = fields.Char('Street3')
    cal_zip = fields.Char('Zip', change_default=True, size=5)
    cal_city = fields.Char('City')
    cal_state_id = fields.Many2one("res.country.state", string='State')
    cal_country_id = fields.Many2one('res.country', string='Country')
    shedular = fields.Selection([('meeting','Meeting'),('call','Call')], string="Schedular")
    call_datetime = fields.Datetime("Datetime")
