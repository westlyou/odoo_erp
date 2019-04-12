from odoo import models, fields, api


class HrApplicantEduDetail(models.Model):
	_name = "hr.applicant.edu.detail"
	_rec_name = "qualification_id"
	
	qualification_id = fields.Many2one(
		'hr.recruitment.degree',
		string='Qualififcation',
		required=True,
	)
	board_uni = fields.Char(
		string='Board University',
		required=True,
	)
	location = fields.Text(
		string='Location',
	)
	marks_obtain = fields.Float(
		string='Marks Obtain',
	)
	percent_obtain = fields.Float(
		string='Percent Obtain',
	)
	applicant_id = fields.Many2one(
		'hr.applicant',
		string='Application',
	)

