from odoo import models, fields, api


class EmpQualification(models.Model):
	_name = 'emp.ent.qualification'
	
	name = fields.Char(
		string='Name',
		required=True,
	)
	
		



