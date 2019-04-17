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
	applicant_gender = fields.Selection(
		selection=[
			('male','Male'),
			('female','Female'),
			('other','Other')],
		string='Gender',
	)
	applicant_image = fields.Binary(
		string='Image',
	)
	is_need_skype = fields.Boolean(
		string="Need Skype",
		help="Check if Position is out of Ahmedabad",
	)
	skype_id = fields.Char(
		string="Skype Id",
	)
	skype_availability = fields.Datetime(
		string="Skype Availablity",
	)
	availability_to = fields.Date(
		string="Availability TO",
	)
	availability_time_from = fields.Float(
		string='Availability Time From',
	)
	availability_time_to = fields.Float(
		string='Availability Time To',
	)

	presentation_skill = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string='Presentation Skill',
	)
	understanding_position = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Candidate's Understanding of the position",
	)
	background_skill_set = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Relevant Background/Special Skill set",
	)
	professionla_impression = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Professionla Impression",
	)
	motivation_initiative = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Motivation/Initiative",
	)
	interpersonal_skill = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Interpersonal/Communication Skills",
	)
	applicant_flexibility = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Flexibility",
	)
	organizational_fit = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Organizational Fit",
	)
	overall_evaluation = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Overall Evaluation",
	)
	test_marks = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Test Marks",
	)
	email_communication = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Email Communication",
	)
	quickbook_tax_evaluation = fields.Selection(
		selection=[
			('',''),
			('1','Unable to determine or not applicable to this candidate'),
			('2','Below Average - Does not meet requirement'),
			('3','Competent - Acceptable proficiency'),
			('4','Excellent - esceeds requirement'),
			('5','Outstanding'),
		],
		string="Quick Book/Tax software evaluation",
	)
	
	agreement_sign_ask = fields.Selection(
		selection=[
			('ready', 'Ready'),
			('not_ready', 'Not Ready'),
			('not_decided','Not Decided'),
		],
		string='Agreement',
	)
	applicant_communication = fields.Selection(
		selection=[
			('below_average', 'Below Average'),
			('average', 'Average'),
			('good', 'Good'),
			('excellent', 'Excellent'),
		],
	)
	notice_period = fields.Integer(
		string='Notice Period',
	)
	expexted_joining_date = fields.Date(
		string='Expected Joining Date',
	)
	three_month_training = fields.Char(
		string='3 Months Training',
	)
	reason_for_change = fields.Text(
		string='Reason For Change',
	)
	family_background = fields.Text(
		string='Family Background',
	)
	special_comment = fields.Text(
		string='Comments',
	)
	is_mail_sent = fields.Boolean(
		string='Is Mail Sent',
	)
	is_hr_round_interview = fields.Boolean(
		string='Hr Round Interview',
	)


	@api.depends('date_of_birth')
	def _compute_applicant_age(self):
		for rec in self:
			if rec.date_of_birth:
				rec.applicant_age = int((fields.Date.from_string(fields.Date.today()) - fields.Date.from_string(rec.date_of_birth)).days / 365.25)
			
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
	
	@api.multi
	def send_applicant_email_confirmation(self):
		#template_id = self.env.ref("ent_odoo_hr_recruitment_process.email_template_application_confirmation")
		self.ensure_one()
		ir_model_data = self.env['ir.model.data']
		try:
			template_id = ir_model_data.get_object_reference('ent_odoo_hr_recruitment_process', 'email_template_application_confirmation')[1]
		except ValueError:
			template_id = False
		try:
			compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
		except ValueError:
			compose_form_id = False
		ctx = dict()
		ctx.update({
			'default_model': 'hr.applicant',
			'default_applicant_id': self.ids[0],
			'default_use_template': bool(template_id),
			'default_template_id': template_id,
			'default_composition_mode': 'comment',
			'mark_application_as_sent': True,
		})
		return {
			'type': 'ir.actions.act_window',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'mail.compose.message',
			'views': [(compose_form_id, 'form')],
			'view_id': compose_form_id,
			'target': 'new',
			'context': ctx,
		}
		#print ("&&&&&&&&&&&&&&&&&&&",template_id)
		#send_email = template_id.send_mail(self.id)
		#if send_email:
		#	stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Mail Confirmation Sent')])
		#	self.write({
		#		'stage_id': stage_id.id,
		#		'is_mail_sent': True,
		#	})

	@api.multi
	def write(self, vals):
		if 'stage_id' in vals and vals.get('stage_id'):
			stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'HR Round of Interview')])
			for rec in self:
				if stage_id.id == vals.get('stage_id'):
					vals.update({
						'is_hr_round_interview' : True,					
					})
		return super(HrApplicant, self).write(vals)
			
