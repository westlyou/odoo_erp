from odoo import http
from odoo.http import request


class LeadSignup(http.Controller):

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
		print "*****************************kw",kw
		values = {}
		cmr_lead_obj = request.env['crm.lead'].sudo()
		crm_lead_ids = cmr_lead_obj
		if 'email' in kw and kw.get("email"):
			crm_lead_ids = cmr_lead_obj.search([('email_from', '=', kw.get("email"))], limit=1)
		if crm_lead_ids:
			values.update({
				'crm_lead_id': crm_lead_ids,
			})
		print (":::::::::::::::::::cmr_lead_obj",values)
		values = self._prepare_lead_agreement_signup_values(values)
		return request.render("ent_lead_signup.ent_lead_agreement_signup",values)
			
