from odoo import models, fields, api


class Employee(models.Model):
	_inherit = "hr.employee"
	
	date_of_joining = fields.Date(
		string='DOJ',
	)
	available_till_to = fields.Float(
		string='Available To',
	)
	landline_no = fields.Char(
		string='Landline',
	)
	package = fields.Float(
		string='Package (CTC)',
	)
	employee_code = fields.Char(
		string='Employee Code',
	)
	qualification = fields.Char(
		string='Qualification',
	)
	emp_attachment_ids = fields.One2many(
		'emp.attachment.doc',
		'employee_id',
		string='Attachements',
	)
	
	#REMAIN
	#Employee Code SEQUENCE NUMBER, Qualification, Previous Company Data
		
