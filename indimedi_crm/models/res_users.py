# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError


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
        user_id = self.env['res.users'].sudo().with_context({'no_smtp': True}).create(vals)
        user_id.groups_id = [(6,0, [portal, portal_agreement])]
        self.is_user_created = True

class Users(models.Model):
    _inherit = 'res.users'
    
    is_client = fields.Boolean(string="Client")
    
    
    

