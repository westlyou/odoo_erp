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
	
	#FULLY OVERRIDE FOR CHANGE DOMAIN OF THE EQUIPMENT BASED ON EMPLOYEE
	@api.onchange('employee_id', 'department_id')
	def onchange_department_or_employee_id(self):
		domain = []
		if self.department_id:
			domain = [('department_id', '=', self.department_id.id)]
		if self.employee_id and self.department_id:
			domain = ['|'] + domain
		if self.employee_id:
			#domain = domain + ['|', ('employee_id', '=', self.employee_id.id), ('employee_id', '=', None)]
			domain = domain + [('employee_id', '=', self.employee_id.id)]
		equipment = self.env['maintenance.equipment'].search(domain, limit=2)
		if len(equipment) == 1:
			self.equipment_id = equipment
		return {'domain': {'equipment_id': domain}}
    	
