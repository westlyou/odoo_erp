from odoo import http
from odoo.http import request


class LeadSignup(http.Controller):

	LEAD_FIELDS = ['']
	def _prepare_signup_email_val(self, kw):
		return {}

	@http.route(['/website/lead/signup'], type='http', auth="public", website=True)
	def ent_lead_signup(self, **kw):
		values = self._prepare_signup_email_val(kw)
		return request.render("ent_lead_signup.ent_lead_signup_email",values)
	
	def _prepare_lead_agreement_signup_values(self, values):
		return values
	
	@http.route(['/return/lead/signup'], type='http', auth="public", website=True)
	def return_lead_signup(self, **kw):
		values = {}
		cmr_lead_obj = request.env['crm.lead'].sudo()
		crm_lead_ids = cmr_lead_obj
		if 'email' in kw and kw.get("email"):
			crm_lead_ids = cmr_lead_obj.search([('email_from', '=', kw.get("email"))], limit=1)
		lead_primary_contact = request.env['res.partner']
		if crm_lead_ids and crm_lead_ids.child_ids:
			print ("::::::::::::::::::",crm_lead_ids.child_ids)
			lead_primary_contact = crm_lead_ids.child_ids.filtered(lambda ch:ch.primary_contact).sorted()[0]
		if crm_lead_ids:
			values.update({
				'crm_lead_id': crm_lead_ids,
				'lead_primary_contact': lead_primary_contact,
			})
		values = self._prepare_lead_agreement_signup_values(values)
		return request.render("ent_lead_signup.ent_lead_agreement_signup",values)

	def _prepare_primary_contact_vals(kw):
		prim_contact_vals={}
		if 'primary_name' in kw and kw.get('primary_name'):
			prim_contact_vals.update({
				'name': kw.get('primary_name'),
			})
		if 'primary_title' in kw and kw.get('primary_title'):
			partner_title = request.env['res.partner.title'].search([('name', '=', kw.get('primary_title'))], limit=1)
			prim_contact_vals.update({
				'title': partner_title.id,
			})
		if 'primary_mobile' in kw and kw.get('primary_mobile'):
			prim_contact_vals.update({
				'primary_mobile': kw.get('primary_mobile'),
			})
		if 'primary_direct_phone' in kw and kw.get('primary_direct_phone'):
			prim_contact_vals.update({
				'primary_direct_phone': kw.get('primary_direct_phone'),
			})

	def _prepare_job_desc_vals(self, kw):
		job_desc_vals = {}
		if 'hiring_model' in kw and kw.get('hiring_model'):
			job_desc_vals.update({
				'hiring_model': 'permanent',
			})
		if 'seasonal_hour' in kw and kw.get('seasonal_hour'):
			job_desc_vals.update({
				'seasonal_hour': kw.get('seasonal_hour'),
			})
		if 'permanent_hour_selection' in kw and kw.get('permanent_hour_selection'):
			job_desc_vals.update({
				'permanent_hour_selection': kw.get('permanent_hour_selection'),
			})
		if 'rate_per_hour' in kw and kw.get('rate_per_hour'):
			job_desc_vals.update({
				'rate_per_hour': kw.get('rate_per_hour'),
			})
		if 'perm_season_date_from' in kw and kw.get('perm_season_date_from'):
			job_desc_vals.update({
				'perm_season_date_from': kw.get('perm_season_date_from'),
			})
		if 'perm_season_date_to' in kw and kw.get('perm_season_date_to'):
			job_desc_vals.update({
				'perm_season_date_to': kw.get('perm_season_date_to'),
			})
		if 'hiring_model_temporary' in kw and kw.get('hiring_model_temporary'):
			job_desc_vals.update({
				'hiring_model': 'temporary',
			})
		if 'temporary_hour_selection' in kw and kw.get('temporary_hour_selection'):
			job_desc_vals.update({
				'temporary_hour_selection': kw.get('temporary_hour_selection'),
			})
		if 'hiring_model_ondemand' in kw and kw.get('hiring_model_ondemand'):
			job_desc_vals.update({
				'hiring_model': 'On Demand',
			})
		if 'number_of_hour_on_demand_update' in kw and kw.get('number_of_hour_on_demand_update'):
			job_desc_vals.update({
				'number_of_hour_on_demand_update': kw.get('number_of_hour_on_demand_update'),
			})
		if 'profile' in kw and kw.get('profile'):
			profile_id = request.env['job.profile'].search([('name', '=', kw.get('profile'))], limit=1)
			job_desc_vals.update({
				'job_profile_id': profile_id.id,
			})
		if 'experiance' in kw and kw.get('experiance'):
			experiance_id = request.env['job.experiance'].search([('name', '=', kw.get('experiance'))])
			job_desc_vals.update({
				'experiance_id': experiance_id.id,
			})
		if 'task_tobe_done' in kw and kw.get('task_tobe_done'):
			job_desc_vals.update({
				'task_tobe_done': kw.get('task_tobe_done'),
			})
		if 'task_tobe_done2' in kw and kw.get('task_tobe_done2'):
			job_desc_vals.update({
				'task_tobe_done2': kw.get('task_tobe_done2'),
			})
		if 'task_tobe_done3' in kw and kw.get('task_tobe_done3'):
			job_desc_vals.update({
				'task_tobe_done3': kw.get('task_tobe_done3'),
			})
		if 'task_tobe_done4' in kw and kw.get('task_tobe_done4'):
			job_desc_vals.update({
				'task_tobe_done4': kw.get('task_tobe_done4'),
			})
		if 'reporting_id' in kw and kw.get('reporting_id'):
			reporting_id = request.env['res.partner'].search([('name', '=', kw.get('reporting_id'))])
			job_desc_vals.update({
				'reporting_id': reporting_id.id,
			})
		if 'timezone' in kw and kw.get('timezone'):
			timezone_id = request.env['working.timezone'].search([('name', '=', kw.get('timezone'))])
			job_desc_vals.update({
				'timezone_id': timezone_id.id,
			})
		if 'timefrom' in kw and kw.get('timefrom'):
			time_from_id = request.env['from.timezone'].search([('name','=', kw.get('timefrom'))])
			job_desc_vals.update({
				'from_timezone_id': time_from_id.id,
			})
		if 'timeto' in kw and kw.get('timeto'):
			time_to_id = request.env['to.timezone'].search([('name','=', kw.get('timeto'))])
			job_desc_vals.update({
				'to_timezone_id': time_to_id.id,
			})
		return job_desc_vals

	def _prepare_lead_vals(self, kw):
		lead_vals = {}
		if 'name' in kw and kw.get('name'):
			lead_vals.update({
				'name': kw.get('name'),
			})
		if 'c_street' in kw and kw.get('c_street'):
			lead_vals.update({
				'c_street': kw.get('c_street'),
			})
		if 'c_street3' in kw and kw.get('c_street3'):
			lead_vals.update({
				'c_street3': kw.get('c_street3'),
			})
		if 'c_city' in kw and kw.get('c_city'):
			lead_vals.update({
				'c_city': kw.get('c_city'),
			})
		
		if 'c_state_id' in kw and kw.get('c_state_id'):
			state_id = request.env['res.country.state'].search([('name', '=' , kw.get('c_state_id'))], limit=1)
			print ("::::::::::::::::state_id",state_id)
			lead_vals.update({
				'c_state_id': state_id.id,
			})
		
		if 'c_zip' in kw and kw.get('c_zip'):
			lead_vals.update({
				'c_zip': kw.get('c_zip'),
			})
		
		if 'phone' in kw and kw.get('phone'):
			lead_vals.update({
				'phone': kw.get('phone'),
			})
		
		if 'lead_ext' in kw and kw.get('lead_ext'):
			lead_vals.update({
				'lead_ext': kw.get('lead_ext'),
			})
		
		if 'email_from' in kw and kw.get('email_from'):
			lead_vals.update({
				'email_from': kw.get('email_from'),
			})
		return lead_vals
		
		
		
		
		

	@http.route(['/submit/lead/signup'], type='http', auth="public", website=True)
	def submit_lead_signup(self, **kw):
		print "kw---------------------------------",kw
		job_description_vals = self._prepare_job_desc_vals(kw)
		lead_vals = self._prepare_lead_vals(kw)
		if 'lead_id' in kw and kw.get('lead_id'):
			lead_id = request.env['crm.lead'].search([('id', '=', kw.get('lead_id'))])
			#lead_primary_contact_id = lead_id.child_ids.filtered(lambda ch:ch.primary_contact).sorted()[0]
			#prim_contact_vals = self._prepare_primary_contact_vals(kw)
			#lead_primary_contact_id.write(prim_contact_vals)
			lead_id.write(lead_vals)
			if lead_id.job_description_ids:
				lead_id.job_description_ids[0].write(job_description_vals)
