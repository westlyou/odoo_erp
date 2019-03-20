from odoo import models, fields, api


class PopupMassage(models.TransientModel):
    _name = 'popup.massage'
    
    name = fields.Char("Massage")
    