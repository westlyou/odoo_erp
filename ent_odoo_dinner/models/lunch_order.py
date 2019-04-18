from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Order(models.Model):
	_inherit = "lunch.order"
	
	@api.constrains('user_id', 'date')
	def _check_uniq_for_date(self):
		for order in self:
			lunch_order = self.env['lunch.order'].search([('user_id', '=', self.env.uid), ('date', '=', order.date)])
			print ("::::::::::::::::::::::::lunch_order",fields.Datetime.now())
			if lunch_order:
				raise ValidationError("Cannot create new order for same date")
