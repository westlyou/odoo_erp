from odoo import models, fields, api


class HrApplicant(models.Model):
	_inherit = "hr.applicant"
	
	applicant_title = fields.Selection(
		selection=[
			('mr','Mr.'),
			('mrs','Mrs.'),
			('ms','Ms'),
		],
		string='Title',
	)
	first_name = fields.Char(
		string='First Name',
		website_form_blacklisted=False,
	)
	middle_name = fields.Char(
		string='Middle Name',
	)
	last_name = fields.Char(
		string='Last Name',
	)
	date_of_birth = fields.Date(
		string='Date of Birth',
	)
	nationality = fields.Char(
		string='Nationality',
	)
	applicant_age = fields.Char(
		string='Age',
		compute='_compute_applicant_age',
		store=True,
	)
	phone_std = fields.Integer(
		string="STD",
	)
	known_language_ids = fields.Many2many(
		'res.lang',
		string="Languages Known",
	)
	marital_status = fields.Selection(
		selection=[
			('married','Married'),
			('single','Single'),
		],
		string='Marital Status',
	)
	blood_group = fields.Char(
		string='Blood Group',
	)
	present_f_add = fields.Char(
		string='Address Line 1',
	)
	present_s_add = fields.Char(
		string='Address Line 2',
	)
	present_area = fields.Char(
		string='Area',
	)
	present_city = fields.Char(
		string='City',
	)
	present_state_id = fields.Many2one(
		'res.country.state',
		string='State',
	)
	present_country_id = fields.Many2one(
		'res.country',
		string='Country',
	)
	present_zip = fields.Char(
		string='Pin Code',
	)
	same_as_above = fields.Boolean(
		string='Same As Present Address',
	)
	
	perma_f_add = fields.Char(
		string='Address Line 1',
	)
	perma_s_add = fields.Char(
		string='Address Line 2',
	)
	perma_area = fields.Char(
		string='Area',
	)
	perma_city = fields.Char(
		string='City',
	)
	perma_state_id = fields.Many2one(
		'res.country.state',
		string='State',
	)
	perma_country_id = fields.Many2one(
		'res.country',
		string='Country',
	)
	perma_zip = fields.Char(
		string='Pin Code',
	)
	edu_applicant_detail_ids = fields.One2many(
		'hr.applicant.edu.detail',
		'applicant_id',
		string='Education Details',
	)
	employeement_history_ids = fields.One2many(
		'employeement.history',
		'applicant_id',
		string='Employee Ment History',
	)


	@api.depends('date_of_birth')
	def _compute_applicant_age(self):
		for rec in self:
			if rec.date_of_birth:
				rec.applicant_age = fields.Date.today() - rec.date_of_birth
			
	@api.onchange('same_as_above')
	def _onchange_same_as_above(self):
		if self.same_as_above:
			self.perma_f_add = self.present_f_add
			self.perma_s_add = self.present_s_add
			self.perma_area = self.present_area
			self.perma_city = self.present_city
			self.perma_state_id = self.present_state_id.id
			self.perma_country_id = self.present_country_id.id
			self.perma_zip = self.present_zip
