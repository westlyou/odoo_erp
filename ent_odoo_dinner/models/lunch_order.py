from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import time
import pytz


class Order(models.Model):
	_inherit = "lunch.order"
	
	@api.onchange('user_id')
	def _onchange_user_id(self):
		if self.user_id and self.user_id.id != self.env.uid and not self.env.user.has_group("lunch.group_lunch_manager"):
			raise ValidationError("You are not allowed to create another user's dinner")
	
	@api.model
	def create(self, vals):
		if 'user_id' in vals and vals.get('user_id'):
			if vals.get('user_id') != self.env.uid and not self.env.user.has_group("lunch.group_lunch_manager"):
				raise ValidationError("You are not allowed to create another user's dinner")
		return super(Order, self).create(vals)
	
	@api.multi
	def write(self, vals):
		if 'user_id' in vals and vals.get('user_id'):
			if vals.get('user_id') != self.env.uid and not self.env.user.has_group("lunch.group_lunch_manager"):
				raise ValidationError("You are not allowed to create another user's dinner")
		return super(Order, self).write(vals)
		
	
	@api.constrains('user_id', 'date')
	def _check_uniq_for_date(self):
		for order in self:
			lunch_order = self.env['lunch.order'].search([('user_id', '=', self.env.uid), ('date', '=', order.date),('id', '!=', order.id)])
			today_date = datetime.now()
# 			timezone = pytz.timezone('UTC')
# 			today_date = pytz.UTC.localize(today_date)
# 			today_date = today_date.astimezone(timezone)
			if not self.env.user.has_group("lunch.group_lunch_manager"):
				print"first================",today_date.time().strftime("%H:%M:%S") , time.strftime("04:00:00")
				print"=============================",today_date.time().strftime("%H:%M:%S"), time.strftime("13:00:00")
				if today_date.time().strftime("%H:%M:%S") < time.strftime("04:00:00") or today_date.time().strftime("%H:%M:%S") > time.strftime("1:00:59"):
					raise ValidationError("It's too late to order your food")
			if lunch_order:
				raise ValidationError("Cannot create new order for same date")

