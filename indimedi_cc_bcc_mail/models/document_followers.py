# -*- coding: utf-8 -*-

from odoo import api, fields, models


class DocumentFollowers(models.Model):
    _name = 'document.followers'
    _rec_name = 'model_id'
    _description = 'Document Followers'

    model_id = fields.Many2one(
        'ir.model', string='Model')    
    auto_add_followers = fields.Boolean(string="Auto Add Followers")
    internal_follower_ids = fields.Many2many(
        'res.users','res_users_int_followers_rel','doc_follower_id','user_id', string='Internal Followers')
    external_follower_ids = fields.Many2many(
        'res.users','res_users_ext_followers_rel','doc_follower_id','user_id', string='External Followers')