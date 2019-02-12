from odoo import api, fields, models, _


class SubsidiaryMaster(models.Model):
    _name = 'subsidiary.master'
    
    name = fields.Char(string="Name", required=True)