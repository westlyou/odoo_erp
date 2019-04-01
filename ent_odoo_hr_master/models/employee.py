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
		default="New",
		copy=False,
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
	#REMAIN
	#Employee Code SEQUENCE NUMBER, Qualification, Previous Company Data
	
	
	@api.model
	def create(self, vals):
		emp_number = self.env['ir.sequence'].next_by_code('hr.employee.ent.code')	
		if emp_number:
			vals.update({
				'emp_number': emp_number,
			})
		return super(Employee, self).create(vals)
