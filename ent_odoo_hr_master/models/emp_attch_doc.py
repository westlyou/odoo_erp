# -*- coding: utf-8 -*-

from odoo import models, fields


class EmpAttachDoc(models.Model):
	_name = "emp.attachment.doc"
	_description = "Document"
	
	attachment_type_id = fields.Many2one(
		'emp.attachment.type',
		string='Attachment Name',
		required=True,
	)
	attachment_file_name = fields.Binary(
		string='Attachment',
	)
	datas_fname = fields.Char(
		string='File Name',
	)
	is_attached = fields.Boolean(
		string='Attached',
	)
	employee_id = fields.Many2one(
		'hr.employee',
		string='Employee',
	)


class AttachmentType(models.Model):
	_name = "emp.attachment.type"
	
	name = fields.Char(
		string="Name",
		required=True,
	)
