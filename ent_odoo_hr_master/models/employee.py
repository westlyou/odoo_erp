# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


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
		string='Emp Number',
		copy=False,
		#readonly=True,
		default='New',
	)
	qualification = fields.Char(
		string='Qualification',
	)
	previous_company_data = fields.Char(
		string='Previous Company Data',
	)
	emp_qualification_ids = fields.Many2many(
		'emp.ent.qualification',
		string='Qualifications',
	)
	emp_prev_company_ids = fields.One2many(
		'emp.ent.prev.company',
		'employee_id',
		string='Previous Company Data',
	)
	
	date_of_resign = fields.Date(
		string='DOR',
	)
	esic_deduction = fields.Boolean(
		string='ESIC Deduction',
	)
	pf_deduction = fields.Boolean(
		string='PF Deduction',
	)
	blood_group = fields.Char(
		string='Blood Group',
	)
	emp_zip = fields.Char(
		size=6,
	)
	
	emp_full_name = fields.Char(
		string='Full Name',
	)
	father_name = fields.Char(
		string='Father Name',
	)
	date_of_offer = fields.Date(
		string='DOO',
	)
	age = fields.Integer(
		string='Age',
		compute='_compute_emp_age',
		store=True,
	)
	experience = fields.Char(
		string='Experience',
	)
	appleft = fields.Char(
		string='App Left',
	)
	joining_sheet = fields.Binary(
		string='Joining Sheet',
	)
	
	emp_perm_street = fields.Char(
		string="Permanent Address 1",
	)
	emp_perm_street2 = fields.Char(
		string="Permanent Address 2",
	)
	emp_perm_street3 = fields.Char(
		string="Permanent Address 3",
	)
	emp_perm_zip = fields.Char(
		string="Permanent Zip",
	)
	emp_perm_city = fields.Char(
		string="Permanent City",
	)
	emp_perm_state_id = fields.Char(
		string="Permanent State",
	)
	emp_perm_country_id = fields.Char(
		string="Permanent Country",
	)
	
	@api.depends('birthday')
	def _compute_emp_age(self):
		for rec in self:
			if rec.birthday:
				days_in_year = 365.2425
				age= int((fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(rec.birthday)).days / days_in_year)
				rec.age = age
	#@api.model
	#def create(self, vals):
	#	emp_number = self.env['ir.sequence'].next_by_code('hr.employee.ent.code')	
	#	if emp_number:
	#		vals.update({
	#			'emp_number': emp_number,
	#		})
	#	return super(Employee, self).create(vals)
