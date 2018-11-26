# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime


class Feedback(models.Model):
	_name = 'customer.feedback'


	name = fields.Text('Description')
	customers = fields.Many2one('res.partner',string="Contacts")
	date = fields.Date(string="Date",default=fields.Date.context_today)
	feedback_user = fields.Many2one('res.users', string="User", default=lambda self: self.env.user)
	feedback_attachment = fields.Binary(string='Upload File')
	feedback_attachments_fname = fields.Char(string="Attachment Name",store=True)
	