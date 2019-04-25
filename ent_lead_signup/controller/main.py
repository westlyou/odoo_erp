from odoo import http
from odoo.http import request
import base64


class LeadSignup(http.Controller):

	LEAD_FIELDS = ['']
	def _prepare_signup_email_val(self, kw):
		
		return {}

	@http.route(['/website/lead/signup'], type='http', auth="public", website=True)
	def ent_lead_signup(self, **kw):
		values = self._prepare_signup_email_val(kw)
		return request.render("ent_lead_signup.ent_lead_signup_email",values)
	
	def _prepare_lead_agreement_signup_values(self, values):
		title_ids = request.env['res.partner.title'].sudo().search([])
		values.update({
			'title_ids': title_ids,
		})
		
		state_ids = request.env['res.country.state'].sudo().search([])
		values.update({
			'state_ids': state_ids,
		})
		
		profile_ids = request.env['job.profile'].sudo().search([])
		values.update({
			'profile_ids': profile_ids,
		})
		
		experience_ids = request.env['job.experience'].sudo().search([])
		values.update({
			'experience_ids': experience_ids,
		})
		
		reporting_ids = request.env['res.partner'].search([])
		values.update({
			'reporting_ids': reporting_ids,
		})
		
		timezone_ids = request.env['working.timezone'].search([])
		values.update({
			'timezone_ids': timezone_ids,
		})
		
		time_from_ids = request.env['from.timezone'].search([])
		values.update({
			'time_from_ids': time_from_ids,
		})
		
		time_to_ids = request.env['to.timezone'].search([])
		values.update({
			'time_to_ids': time_to_ids,
		})
		nature_experience_ids = request.env['nature.experience'].search([])
		values.update({
			'nature_experience_ids': nature_experience_ids,
		})
		s_tax_id_ids = request.env['tax.software'].search([])
		values.update({
			's_tax_id_ids': s_tax_id_ids,
		})
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
			lead_primary_contact = crm_lead_ids.child_ids.filtered(lambda ch:ch.primary_contact).sorted()
			if lead_primary_contact:
				lead_primary_contact = lead_primary_contact[0]
		if crm_lead_ids:
			values.update({
				'crm_lead_id': crm_lead_ids,
				'lead_primary_contact': lead_primary_contact,
			})
			values = self._prepare_lead_agreement_signup_values(values)
			return request.render("ent_lead_signup.ent_lead_agreement_signup",values)
		values.update({
			'warn_message': 'Record Not Found!',
		})
		return request.render("ent_lead_signup.ent_signup_warning_template",values)

	def _prepare_primary_contact_vals(self, kw):
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
				'mobile': kw.get('primary_mobile'),
			})
		if 'primary_direct_phone' in kw and kw.get('primary_direct_phone'):
			prim_contact_vals.update({
				'phone': kw.get('primary_direct_phone'),
			})
		return prim_contact_vals

	def _prepare_job_desc_vals(self, kw):
		job_desc_vals = {}
		if 'hiring_perm' in kw and kw.get('hiring_perm') == 'on':
			job_desc_vals.update({
				'hiring_model': 'permanent',
			})
		if 'seasonal_hour' in kw and kw.get('seasonal_hour'):
			job_desc_vals.update({
				'seasonal_hour': kw.get('seasonal_hour'),
			})
		if 'seasonal_rate_per_hour' in kw and kw.get('seasonal_rate_per_hour'):
			job_desc_vals.update({
				'seasonal_rate_per_hour': kw.get('seasonal_rate_per_hour'),
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
		if 'hiring_model_temporary' in kw and kw.get('hiring_model_temporary') == 'on':
			job_desc_vals.update({
				'hiring_model': 'temporary',
			})
		if 'temporary_hour_selection' in kw and kw.get('temporary_hour_selection'):
			job_desc_vals.update({
				'temporary_hour_selection': kw.get('temporary_hour_selection'),
			})
		if 'hiring_model_ondemand' in kw and kw.get('hiring_model_ondemand') == 'on':
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
			experience_id = request.env['job.experience'].search([('name', '=', kw.get('experiance'))])
			job_desc_vals.update({
				'experience_id': experience_id.id,
			})
		if 'task_tobe_done' in kw and kw.get('task_tobe_done'):
			job_desc_vals.update({
				'task_tobe_done': kw.get('task_tobe_done'),
			})
		if 'task_tobe_done2' in kw and kw.get('task_tobe_done2'):
			job_desc_vals.update({
				'task_to_be_done2': kw.get('task_tobe_done2'),
			})
		if 'task_tobe_done3' in kw and kw.get('task_tobe_done3'):
			job_desc_vals.update({
				'task_to_be_done3': kw.get('task_tobe_done3'),
			})
		if 'task_tobe_done4' in kw and kw.get('task_tobe_done4'):
			job_desc_vals.update({
				'task_to_be_done4': kw.get('task_tobe_done4'),
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
		if 'nature_experience' in kw and kw.get('nature_experience'):
			nature_experiance_lst = kw.get('nature_experience').split(', ')
			nature_experiance_ids = request.env['nature.experience'].search([('name', 'in', nature_experiance_lst)])
			job_desc_vals.update({
				'nature_experience_ids': [(6, 0, nature_experiance_ids.ids)],
			})
		if 's_tax_id_id' in kw and kw.get('s_tax_id_id'):
			s_tax_id_lst = kw.get('s_tax_id_id').split(', ')
			s_tax_id_ids = request.env['tax.software'].search([('name', 'in', s_tax_id_lst)])
			job_desc_vals.update({
				's_tax_id_ids': [(6, 0, s_tax_id_ids.ids)],
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
		job_description_vals = self._prepare_job_desc_vals(kw)
		lead_vals = self._prepare_lead_vals(kw)
		email_ctx = request.context.copy()
		if 'lead_id' in kw and kw.get('lead_id'):
			lead_id = request.env['crm.lead'].search([('id', '=', kw.get('lead_id'))])
			#lead_primary_contact_id = lead_id.child_ids.filtered(lambda ch:ch.primary_contact).sorted()[0]
			lead_primary_contact = lead_id.child_ids
			email_ctx.update({
				'lead_primary_contact': request.env['res.partner'],
			})
			if lead_id.child_ids:
				lead_primary_contact = lead_id.child_ids.filtered(lambda ch:ch.primary_contact).sorted()
				if lead_primary_contact:
					lead_primary_contact = lead_primary_contact[0]
					email_ctx.update({
						'lead_primary_contact': lead_primary_contact,
					})
			if lead_primary_contact:
				prim_contact_vals = self._prepare_primary_contact_vals(kw)
				lead_primary_contact.write(prim_contact_vals)
			lead_id.write(lead_vals)
			email_ctx.update({
				'job_description': request.env['job.description'],
			})
			if lead_id.job_description_ids:
				lead_id.job_description_ids[0].write(job_description_vals)
				email_ctx.update({
					'job_description': lead_id.job_description_ids[0],
				})
			email_ctx.update({
				'signup_email_cc': '',
			})
			if lead_id.company_id.signup_email_cc:
				sign_up_email_cc = ', '.join([signup_user_cc.email for signup_user_cc in lead_id.company_id.signup_email_cc])
				email_ctx.update({
					'signup_email_cc': sign_up_email_cc,
				})
			
			email_template_id = request.env.ref("ent_lead_signup.email_template_lead_signup_confirmation")
			email_template_id.with_context(email_ctx).send_mail(lead_id.id)
		return request.redirect("/submit/signup/success")
		
	@http.route(['/submit/signup/success'], type='http', auth="public", website=True)
	def signup_submit_success(self, **kwargs):
		return request.render("ent_lead_signup.sugnup_success_sent")

	@http.route(['/accept/lead/signup'], type='json', auth="public", website=True)
	def payment_transaction(self, **kwargs):
		if 'lead_id' in kwargs and kwargs.get("lead_id"):
			lead_id = request.env['crm.lead'].search([('id', '=', kwargs.get("lead_id"))])
			
			pdf = lead_id.company_id.signup_tc
			pdfhttpheaders = [
				('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
				('Content-Disposition', 'attachment; filename=Invoice.pdf;')
			]
			return http.request.make_response(pdf, headers=pdfhttpheaders)
		return {"crm_url":True}
	
	@http.route(['/accept/lead/signup/http'], type='http', auth="public", website=True)
	def payment_transaction_accept(self, **kwargs):
		lead_id = request.env['crm.lead'].search([('id', '=', '28')])
		if lead_id.company_id.signup_tc:
			pdf = base64.b64decode(lead_id.company_id.signup_tc)
			pdfhttpheaders = [
				('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
				('Content-Disposition', 'attachment; filename=Invoice.pdf;')
			]
		return request.make_response(pdf, headers=pdfhttpheaders)
