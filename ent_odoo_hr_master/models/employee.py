# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
	_inherit = "hr.employee"
	
	date_of_joining = fields.Date(
		string='DOJ',
	)
	available_till_to = fields.Float(
		string='Available Till',
	)
	landline_no = fields.Char(
		string='Landline',
	)
	package = fields.Float(
		string='Package (CTC)',
	)
	qualification = fields.Char(
		string='Qualification',
	)
	emp_attachment_ids = fields.One2many(
		'emp.attachment.doc',
		'employee_id',
		string='Attachements',
	)
	emp_number = fields.Char(
		string="Emp Number",
		copy=False,
		readonly=True,
		default='New',
	)
	qualification = fields.Char(
		string='Qualification',
	)
	previous_company_data = fields.Char(
		string="Previous Company Data",
	)
	emp_qualification_ids = fields.Many2many(
		'emp.ent.qualification',
		string="Qualifications",
	)
	emp_prev_company_ids = fields.One2many(
		'emp.ent.prev.company',
		'employee_id',
		string='Previous Company Data',
	)
	
	date_of_resign = fields.Date(
		string="DOR",
	)
	esic_deduction = fields.Boolean(
		string="ESIC Deduction",
	)
	pf_deduction = fields.Boolean(
		string="PF Deduction",
	)
	blood_group = fields.Char(
		string="Blood Group",
	)
	emp_zip = fields.Char(
		size=6,
	)
	
	
	@api.model
	def create(self, vals):
		emp_number = self.env['ir.sequence'].next_by_code('hr.employee.ent.code')	
		if emp_number:
			vals.update({
				'emp_number': emp_number,
			})
		return super(Employee, self).create(vals)
