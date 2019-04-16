from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class PaymentMethodCustom(models.Model):
    _name = 'payment.method.custom'

    name = fields.Char(string="Name", required=True)