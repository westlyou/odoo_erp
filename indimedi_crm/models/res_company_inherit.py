# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    signup_tc = fields.Binary(string="Signup T&C File", attachment=True)
    filename = fields.Char(string="FIle Name")
    signup_email_cc = fields.Many2many('res.partner', 'rel_signup_email_cc')
    staff_confirmation_email_cc = fields.Many2many('res.partner', 'rel_staff_confirmation_email_cc')
    