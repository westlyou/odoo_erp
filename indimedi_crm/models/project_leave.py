from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

class ProjectLeave(models.Model):
    _name = 'project.leave'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    
    name = fields.Many2one('project.task', string="Client", required=True)
    project_id = fields.Many2one(related='name.project_id', string="Project", copy=False)
    contact_name = fields.Char(compute='_get_customer_primary_contact', string="Contact", copy=False)
    invoicing_type_id = fields.Many2one(related='project_id.invoicing_type_id', string="Invoicing Type")
    hour_selection = fields.Selection(related='project_id.hour_selection', string="Working Hours", copy=False)
    min_hour_per_day = fields.Float(compute='_get_min_hour_per_day', string="Min Hour/Day", copy=False)
    us_name_id = fields.Many2one(related='project_id.jd_us_name_id', string="US Name", copy=False)
    start_date = fields.Date(string="Start Date", required=True, default=fields.Datetime.now)
    end_date = fields.Date(string="End Date", required=True, default=fields.Datetime.now)
    leave_duration = fields.Integer(string="Leave Duration(Hour)", required=True, copy=False)
    reason = fields.Text(string="Reason for Leave")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('sent', 'Sent')], string="State", 
                              default='draft', copy=False)
    local_start_date = fields.Char(compute='_convert_to_new_date_formate')
    
    
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for holiday in self:
            domain = [
                ('start_date', '<=', holiday.end_date),
                ('end_date', '>=', holiday.start_date),
                ('name', '=', holiday.name.id),
                ('id', '!=', holiday.id),
            ]
            nholidays = self.search(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on same day!'))

    
    @api.multi
    @api.depends('start_date', 'end_date')
    def _convert_to_new_date_formate(self):
        for rec in self:
            if rec.start_date:
                start_date = datetime.strptime(rec.start_date, DEFAULT_SERVER_DATE_FORMAT)
                start_date = datetime.strftime(start_date, '%B %d %Y')
#                 rec.local_start_date = start_date
            if rec.end_date:
                end_date = datetime.strptime(rec.end_date, DEFAULT_SERVER_DATE_FORMAT)
                end_date = datetime.strftime(end_date, '%B %d %Y')
#                 rec.local_start_date = start_date
            if self.start_date == self.end_date:
                rec.local_start_date = start_date
                
            if self.start_date and self.end_date:
                if not self.start_date == self.end_date:
                    rec.local_start_date = "" + start_date + " to " + end_date

    @api.multi
    @api.depends('project_id')
    def _get_customer_primary_contact(self):
        for rec in self:
            name = ''
            if rec.project_id:
                if rec.project_id.partner_id:
                    if rec.project_id.partner_id.child_ids:
                        child_ids = rec.project_id.partner_id.child_ids
                        if child_ids:
                            for contact in child_ids:
                                if contact.primary_contact:
                                    name = contact.name
                            if not name:
                                name = child_ids[0].name
                if not name:
                    name = rec.project_id.partner_id.name
            rec.contact_name = name
                     
    
    @api.onchange('min_hour_per_day')
    def onchange_min_hour_per_day(self):
        self.leave_duration = self.min_hour_per_day
    
    @api.multi
    def copy(self):
        for rec in self:
            raise UserError("Copy operation not allowed.")
        return super(ProjectLeave, self).copy()
    
    @api.multi
    def unlink(self):
        if not self.env.user.id == 1:
            for rec in self:
                if rec.state == 'sent':
                    raise UserError("You can not delete sent leave request")
        return super(ProjectLeave, self).unlink()
    
    @api.multi
    @api.depends('project_id')
    def _get_min_hour_per_day(self):
        for rec in self:
            min_hour = 0
            if rec.invoicing_type_id.name in ['Monthly', 'Monthly Advance']:
                min_hour = (float(rec.project_id.hour_selection) / 4)
            if rec.invoicing_type_id.name in ['Weekly', 'Weekly Advance']:
                min_hour = float(rec.project_id.hour_selection)
                
            hour_per_day = 0
            if min_hour > 0:
                hour_per_day = float(min_hour) / 5
            
            rec.min_hour_per_day = hour_per_day
            
    @api.multi
    def action_confirm_leave(self):
        
        if self.end_date < self.start_date:
            raise UserError("End date should not less then start date.")
        if self.leave_duration <= 0:
            raise UserError("Zero or negative duration is not allowed.")
        
        self.state = 'confirm'
        
        
    @api.multi
    def action_send_leave_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_project_leave_request')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        server_id = self.env.user.mail_server_id.id
        ctx.update({
            'default_model': 'project.leave',
            'default_res_id': self.ids[0],
            'default_partner_ids':[(6,0,self.name.partner_ids.ids)],
            'default_email_cc':[(6,0,self.name.cc_partner_ids.ids)],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_mail_server_id': server_id,
        })
        return {
            'name': _('Project Leave Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
#         ctx.update({
#             'default_model': 'project.leave',
#             'default_res_id': self.ids[0],
#             'default_partner_ids':[(6,0,self.name.partner_ids.ids)],
#             'default_use_template': bool(template_id),
#             'default_template_id': template_id,
#             'default_composition_mode': 'comment',
#             'default_mail_server_id': server_id,
#         })
#         return {
#             'name': _('Project Leave Email'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form_id, 'form')],
#             'view_id': compose_form_id,
#             'target': 'new',
#             'context': ctx,
#         }
        
     
        
class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def mail_project_leave_on_send(self):
        if not self.filtered('subtype_id.internal'):
            leave = self.env['project.leave'].browse(self._context['default_res_id'])
            leave.state = 'sent'

    @api.multi
    def send_mail(self, auto_commit=False):
        if self._context.get('default_model') == 'project.leave' and self._context.get('default_res_id'):
            self = self.with_context(mail_post_autofollow=True)
            self.mail_project_leave_on_send()
        return super(MailComposeMessage, self).send_mail(auto_commit=auto_commit)

        