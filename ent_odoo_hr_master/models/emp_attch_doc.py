from odoo import models, fields


class EmpAttachDoc(models.Model):
	_name = "emp.attachment.doc"
	_description = "Document"
	
	attachment_id = fields.Many2one(
		'ir.attachment',
		string='Attachement',
		required=True,
	)
	is_attached = fields.Boolean(
		string='Attached',
		default=True,
	)
	employee_id = fields.Many2one(
		'hr.employee',
		string='Employee',
	)

