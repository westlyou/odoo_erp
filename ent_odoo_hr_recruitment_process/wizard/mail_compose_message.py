# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'hr.applicant' and self._context.get('default_applicant_id') and self._context.get('mark_application_as_sent'):
            applicant_id = self.env['hr.applicant'].browse([self._context['default_applicant_id']])
            stage_id = self.env['hr.recruitment.stage'].search([('name', '=', 'Mail Confirmation Sent')])
            applicant_id.write({
            	'stage_id': stage_id.id,
            	'is_mail_sent': True,
        	})
            self = self.with_context(mail_post_autofollow=True)
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

