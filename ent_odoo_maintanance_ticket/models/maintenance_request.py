from odoo import models, fields, api


class MaintenanceRequest(models.Model):
	_inherit = "maintenance.request"
	
	name = fields.Char(
		required=False,
	)
	
	@api.onchange('category_id')
	def onchange_category_id(self):
		res = super(MaintenanceRequest, self).onchange_category_id()
		self.name = self.category_id.name or self.equipment_id.name
	
	@api.model
	def default_get(self, fields):
		rec = super(MaintenanceRequest, self).default_get(fields)
		employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
		if employee_id:
			rec.update({
				'employee_id': employee_id.id,
			})
		return rec
