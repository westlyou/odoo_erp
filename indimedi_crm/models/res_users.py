# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now


_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'
    
    is_user_created = fields.Boolean(string="User Created")
    
    @api.multi
    def create_login(self):
        if self.is_user_created:
            raise UserError("User Already created for this contact!")
        if not self.email:
            raise UserError("Contact email required to create user!")
        portal = self.env.ref('base.group_portal').id
        portal_agreement = self.env.ref('indimedi_crm.group_agreement_portal_user').id
        
        vals = {
                'name': self.name,
                'partner_id':self.id,
                'login':self.email,
                'is_client': True
                }
        user_id = self.env['res.users'].sudo().with_context({'no_smtp': True, 'bypass_signup_email': True}).create(vals)
        user_id.groups_id = [(6,0, [portal, portal_agreement])]
#         user_id.action_reset_password()
        self.is_user_created = True

class Users(models.Model):
    _inherit = 'res.users'
    
    is_client = fields.Boolean(string="Client")
    staff_confirm_tc = fields.Binary(string="Staff Confirmation T&C File", attachment=True)
    filename = fields.Char(string="FIle Name")
    
    
#     @api.multi
#     def action_reset_password(self):
#         """ create signup token for each user, and send their signup url by email """
#         # prepare reset password signup
#         create_mode = bool(self.env.context.get('create_user'))
# 
#         # no time limit for initial invitation, only for reset password
#         expiration = False if create_mode else now(days=+1)
# 
#         self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
# 
#         # send email to users with their signup url
#         template = False
#         if create_mode:
#             try:
#                 template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
#             except ValueError:
#                 pass
#         if not template:
#             template = self.env.ref('auth_signup.reset_password_email')
#         assert template._name == 'mail.template'
# 
#         template_values = {
#             'email_to': '${object.email|safe}',
#             'email_cc': False,
#             'auto_delete': True,
#             'partner_to': False,
#             'scheduled_date': False,
#         }
#         
#         template.write(template_values)
# 
#         if not self.env.context.get('bypass_signup_email'):
#             for user in self:
#                 if not user.email:
#                     raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
#                 with self.env.cr.savepoint():
#                     template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
#                 _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
# 
#     

