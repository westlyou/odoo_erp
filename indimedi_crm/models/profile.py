import base64
from odoo import models, fields, api
from odoo import modules
import smtplib

class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self,values):
         # notification field: if not set, set if mail comes from an existing mail.message
        if 'notification' not in values and values.get('mail_message_id'):
            values['notification'] = True
        if not values.get('mail_message_id'):
            self = self.with_context(message_create_from_mail_mail=True)
        res = super(MailMail, self).create(values)
        mail_server_id = self.mail_server_id.search([('smtp_user', '=', res.author_id.email)])[0]
        if mail_server_id:
            res.mail_server_id = mail_server_id.id
        return res

class ResUser(models.Model):
    _inherit = 'res.users'

    # cal_client_id = fields.Char("Client_id")
    # cal_client_secret = fields.Char("Client_key")
    # server_uri = fields.Char('URI for tuto')
    # google_drive_authorization_code = fields.Char(string='Authorization Code')
    # google_drive_uri = fields.Char(compute='_compute_drive_uri', string='URI', help="The URL to generate the authorization code from Google")
    mail_server_id = fields.Many2one('ir.mail_server',string="Outgoing mail server", required=False)
    #outgoing
    smtp_host = fields.Char(related = 'mail_server_id.smtp_host', string='SMTP Server', help="Hostname or IP of SMTP server")
    smtp_port = fields.Integer(related = 'mail_server_id.smtp_port', string='SMTP Port', size=5, help="SMTP Port. Usually 465 for SSL, and 25 or 587 for other cases.")
    smtp_user = fields.Char(related = 'mail_server_id.smtp_user', string='Username', help="Optional username for SMTP authentication")
    smtp_pass = fields.Char(related = 'mail_server_id.smtp_pass', string='Password', help="Optional password for SMTP authentication")
    smtp_encryption = fields.Selection([('none', 'None'),
                                        ('starttls', 'TLS (STARTTLS)'),
                                        ('ssl', 'SSL/TLS')],
                                        related = 'mail_server_id.smtp_encryption',
                                        string='Connection Security', default='none',
                                        help="Choose the connection encryption scheme:\n"
                                            "- None: SMTP sessions are done in cleartext.\n"
                                            "- TLS (STARTTLS): TLS encryption is requested at start of SMTP session (Recommended)\n"
                                            "- SSL/TLS: SMTP sessions are encrypted with SSL/TLS through a dedicated port (default: 465)")
    smtp_debug = fields.Boolean(related = 'mail_server_id.smtp_debug', string='Debugging', help="If enabled, the full output of SMTP sessions will "
                                                         "be written to the server log at DEBUG level "
                                                         "(this is very verbose and may include confidential info!)")
    sequence = fields.Integer(related = 'mail_server_id.sequence', string='Priority', default=10, help="When no specific mail server is requested for a mail, the highest priority one "
                                                                  "is used. Default priority is 10 (smaller number = higher priority)")


    # email = fields.Char(related='smtp_user',string='Email')
    notification_type = fields.Selection([
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in Inodoo')],
        'Notification Management', required=True, default='email',
        help="Policy on how to handle Chatter notifications:\n"
             "- Emails: notifications are sent to your email\n"
             "- Odoo: notifications appear in your Odoo Inbox")

    def set_values(self):
        # super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param
        params = self.env['ir.config_parameter'].sudo()

    @api.model
    def create(self, vals):
        mail_ser_vals = {
            'name': vals.get('name', None),
            'smtp_host': vals.get('smtp_host', None) and vals.pop('smtp_host') or 'smtp',
            'smtp_port': vals.get('smtp_port', None) and vals.pop('smtp_port') or 25,
            'smtp_user': vals.get('smtp_user', None) and vals.pop('smtp_user') or '',
            'smtp_pass': vals.get('smtp_pass', None) and vals.pop('smtp_pass') or '',
            'smtp_encryption': vals.get('smtp_encryption', None) and vals.pop('smtp_encryption') or '',
            'smtp_debug': vals.get('smtp_debug', None) and vals.pop('smtp_debug') or '',
            'sequence': vals.get('sequence', None) and vals.pop('sequence') or '',
        }
        mail_server_id = self.env['ir.mail_server'].create(mail_ser_vals)
        vals.update({'mail_server_id': mail_server_id.id})
        res = super(ResUser, self).create(vals)
        res.sudo().set_values()
        return res

    @api.multi
    def write(self, vals):
        mail_ser_vals = {
            'name': vals.get('name', None) or self.name,
            'smtp_host': vals.get('smtp_host', None) and vals.pop('smtp_host') or self.mail_server_id.smtp_host,
            'smtp_port': vals.get('smtp_port', None) and vals.pop('smtp_port') or self.mail_server_id.smtp_port,
            'smtp_user': vals.get('smtp_user', None) and vals.pop('smtp_user') or self.mail_server_id.smtp_user,
            'smtp_pass': vals.get('smtp_pass', None) and vals.pop('smtp_pass') or self.mail_server_id.smtp_pass,
            'smtp_encryption': vals.get('smtp_encryption', None) and vals.pop('smtp_encryption') or self.mail_server_id.smtp_encryption,
            'smtp_debug': vals.get('smtp_debug', None) and vals.pop('smtp_debug') or self.mail_server_id.smtp_debug,
            'sequence': vals.get('sequence', None) and vals.pop('sequence') or self.mail_server_id.sequence,
        }
        res = super(ResUser, self).write(vals)
        self.sudo().set_values()
        self.mail_server_id.write(mail_ser_vals)
        return res

    # @api.depends('google_drive_authorization_code')
    # def _compute_drive_uri(self):
    #     google_drive_uri = self.env['google.service']._get_google_token_uri('drive', scope=self.env['google.drive.config'].get_google_scope())
    #     for config in self:
    #         config.google_drive_uri = google_drive_uri


    def test_smtp_connection(self):
        return self.mail_server_id.test_smtp_connection()

    @api.onchange('smtp_encryption')
    def _onchange_encryption(self):
        result = {}
        if self.smtp_encryption == 'ssl':
            self.smtp_port = 465
            if not 'SMTP_SSL' in smtplib.__all__:
                result['warning'] = {
                    'title': _('Warning'),
                    'message': _('Your server does not seem to support SSL, you may want to try STARTTLS instead'),
                }
        else:
            self.smtp_port = 25
        return result