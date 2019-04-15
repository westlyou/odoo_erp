from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class AnnEmail(models.Model):
    _name = 'ann.email'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Announcement Email'
    _rec_name = 'template_id'
    
    name = fields.Char(string="Name")
    project_ids = fields.Many2many('project.project', string="Assignment")
    date = fields.Date(string="Date")
    partner_ids = fields.Many2many('res.partner', string="Contacts")
    template_id = fields.Many2one('mail.template', string="Email Template")
    
    project_status = fields.Selection([('is_expired', 'Expired'),
                                       ('on_notice', 'On Notice'),
                                       ('all', 'All Active')])

    @api.onchange('project_status')
    def onchange_project_status(self):
        if self.project_status:
            if self.project_status == 'is_expired':
                return {'domain':{'project_ids':[('is_expired', '=', True)]}}
            
            if self.project_status == 'on_notice':
                return {'domain':{'project_ids':[('on_notice', '=', True)]}}
            if self.project_status == 'all':
                return {'domain':{'project_ids':[('active', '=', True)]}}
        
        
    
    @api.onchange('project_ids')
    def onchange_partner_id(self):
        if not self.project_ids:
            self.partner_ids = False
            return
        
        partner = []
        for project in self.project_ids:
            if project.partner_id:
                if project.partner_id.child_ids:
                    partner += project.partner_id.child_ids.ids
        
        self.partner_ids = [(6,0,partner)]
    
    @api.multi
    def action_send_email(self):
        
                
        ctx = dict(email_from= self.env.user.email,
                        user_name= self.env.user.name,
                        
                        ) #20554 server
       
        ctx.update({
                'default_model': 'ann.email',
                'default_res_id': self.ids[0],
                'default_use_template': bool(self.template_id.id),
                'default_template_id': self.template_id.id,
                'default_composition_mode': 'comment',
                'default_partner_ids': [(6,0, self.partner_ids.ids)],
                'email_to' : self.env.user.email,
        })
            
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id 
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
    
    