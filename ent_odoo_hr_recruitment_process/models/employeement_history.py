from odoo import models, fields, api


class EmployeementHistory(models.Model):
	_name = "employeement.history"

	name = fields.Char(
		string='Name',
		required=True,
	)
	job_title_id = fields.Many2one(
		'hr.job',
		required=True,
	)
	start_date = fields.Date(
		string='Employeement Start Date',
	)
	work_location = fields.Char(
		string='Work Location',
	)
	job_responsability = fields.Text(
		string='Job Responseability',
	)
	#achievements_ids = fields.One2many(
	#	'ir.achievement',
	#	string='Achivements',
	#)
	applicant_id = fields.Many2one(
		'hr.applicant',
		string='Application',
	)
