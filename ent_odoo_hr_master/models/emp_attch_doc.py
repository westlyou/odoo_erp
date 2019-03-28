from odoo import models, fields


class EmpAttachDoc(models.Model):
	_name = "emp.attachment.doc"
	_description = "Document"
	
	doc_type_id = fields.Many2one(
		'emp.doc.type',
		string='Document',
		required=True,
	)
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


class EmpDoc(models.Model):
	_name = "emp.doc.type"
	
	name = fields.Char(
		string='Name',
		required=True,
	)
