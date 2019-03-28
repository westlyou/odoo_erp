# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class Equipment(models.Model):
	_inherit = "maintenance.equipment"
	
	cgst_tax = fields.Float(
		string="CGST",
	)
	sgst_tax = fields.Float(
		string="SGST",
	)
	total_cost = fields.Float(
		string="Total Cost",
		compute="_compute_total_cost",
		store=True,
	)
	system_ip = fields.Char(
		string="IP",
	)
	system_user_name = fields.Char(
		string="User Name",
	)
	system_password = fields.Char(
		string="Password",
	)
	invoice_date = fields.Date(
		string="Invoice Date",
	)
	invoice_value = fields.Char(
		string="Invoice Value",
	)
	is_scrap_system = fields.Boolean(
		string="Is Scrap System",
	)
	tight_vnc_password = fields.Char(
		string="Tight VNC Password",
	)
	system_location = fields.Many2one(
		'res.partner',
		string="Location",
	)
	system_ram = fields.Char(
		string="RAM",
	)
	system_processor = fields.Char(
		string="Processor",
	)
	system_total_disk = fields.Char(
		string="Total Disk",
	)
	system_os = fields.Char(
		string="OS",
	)
	
	
	@api.depends("cgst_tax", "sgst_tax", "cost")
	def _compute_total_cost(self):
		for rec in self:
			rec.total_cost = (rec.cost * (rec.cgst_tax + rec.sgst_tax))/100.00
	
	@api.onchange("is_scrap_system")
	def _onchange_is_scrap_system(self):
		if self.is_scrap_system:
			self.scrap_date = fields.Date.today()
		else:
			self.scrap_date = False
	
	@api.onchange("invoice_date")
	def _onchange_invoice_date(self):
		if self.invoice_date:
			invoice_date = self.invoice_date
			warrenty_date = fields.Date.from_string(invoice_date)
			self.warranty = warrenty_date + relativedelta(years=1)
