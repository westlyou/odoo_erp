from odoo import models, fields, api


class EmpPrevCompany(models.Model):
	_name = "emp.ent.prev.company"
	
	name = fields.Char(
		string='Company Name',
		required=True,
	)
	designation = fields.Many2one(
		'hr.job',
		string='Designation',
		required=True,
	)
	joining_date = fields.Date(
		string='Joining Date',
		required=True,
	)
	resign_date = fields.Date(
		string='Resignation Date',
	)
	employee_id = fields.Many2one(
		'hr.employee',
		string='Employee',
	)
	
		



