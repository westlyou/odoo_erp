# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import datetime
import base64
# import html2text
from base64 import b64encode
from base64 import b64decode
from logging import getLogger
from PIL import Image
from StringIO import StringIO
from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.utils import PdfReadError

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    pass



class ResumeDetails(models.Model):
    _name = 'resume.details'
    _inherit = ['mail.thread']
    _rec_name = 'name'

    job_id = fields.Many2one('hr.employee')
    jd_id = fields.Many2one('job.description')
    name = fields.Char(string="Employee, Profile")
    profile = fields.Many2one('job.profile',string="Profile")
    resume = fields.Html(string='Resume')
    resume_post_sales = fields.Html(string='Resume Sales')
    sourcebl = fields.Binary(string='Class Description')
    datas_attachments = fields.Binary(string='Attachment',store=True)
    datas_attachments_fname = fields.Char(string="Attachment Name",store=True)
    employee_name = fields.Char(string="Employee")
    attachment_id = fields.Many2one('ir.attachment',string="Attachement")


    @api.model
    def create(self, vals):
        res = super(ResumeDetails, self).create(vals)
        # resume_hr = res.resume
        # html_to_text = (html2text.html2text(resume_hr))
        # content = html_to_text.encode('utf-8')
        # res.sourcebl = base64.encodestring(str(content))
        res.employee_name = res.job_id.name
        # attachments = self.env['ir.attachment']
        # attachments.create({'name':str(res.employee_name) + ',' + str(res.profile.name),
        #                     'type':'binary',
        #                     'datas': res.sourcebl, 
        #                     'datas_fname':str(res.employee_name) + ',' + str(res.profile.name) + '.doc', 
        #                     'res_model':'resume.details',
        #                     'res_id':res.id,
        #                     'mimetype':'application/msword'})
        # atts = self.env['ir.attachment'].search([('res_model','=','resume.details'),('res_id','=',res.id)])
        # new_attachment_id = self.env['ir.attachment'].search([],order="id desc",limit=1)
        # res.datas_attachments = new_attachment_id.datas
        # res.datas_attachments_fname = str(res.employee_name) + ',' + str(res.profile.name)  + '.doc'
        # resume_sales = self.env['resume.sales'].create(
        #         {'name':str(res.employee_name) + ',' + str(res.profile.name),
        #         'profile':res.profile.id,
        #         'employee_name':res.employee_name,
        #         'resume':res.resume,
        #         'datas_attachments':res.datas_attachments,
        #         'datas_attachments_fname':res.datas_attachments_fname
        #         })
        # new_resume_id = self.env['resume.sales'].search([],order="id desc",limit=1)
        # attachments.create({'name':str(res.employee_name) + ',' + str(res.profile.name),
        #             'type':'binary',
        #             'datas': res.datas_attachments, 
        #             'datas_fname':res.datas_attachments_fname, 
        #             'res_model':'resume.sales',
        #             'res_id':new_resume_id.id,
        #             'mimetype':'application/msword'})



        # new_attachment_id = self.env['ir.attachment'].search([],order="id desc",limit=1)
        # # new_resume_id.datas_attachments = new_attachment_id.datas
        # # new_resume_id.datas_attachments_fname = new_attachment_id.datas_fname
        # new_resume_id.employee_name = res.employee_name
        


        return res


    @api.onchange('profile')
    def _name_employee(self):
        if self.job_id:
            for rec in self.job_id:
                concat_str = str(rec.name)+ ',' + ' ' +str(self.profile.name)
                self.name = concat_str
                print self.name
                
    # @api.multi
    # def action_resume2_send(self):
    #         '''
    #         for send agreement, here default set tempate permenent 
    #         if hiring model permenent selected and it set temporary if temporary selected. 
    #         {{ DESCRIPTION }}
    #         '''

    #         self.ensure_one()

    #         ir_model_data = self.env['ir.model.data']
    #         template = self.env['mail.template'].create({'model_id':self.env['ir.model'].search([('model', '=', 'resume.details')], limit=1).id,'name':str(self.name),'body_html':self.resume,})               
    #         template_id = template.id
    #         compose_form_ids = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
    #         ctx = dict()
    #         ctx.update({
    #                 'default_model': 'job.description',
    #                 # 'default_res_id': self.ids[0],
    #                 'default_use_template': bool(template_id),
    #                 'default_template_id': template_id,
    #                 'default_composition_mode': 'comment',
    #                 'mark_so_as_sent': True,
    #                 'custom_layout': "email_template_agreement_crm",
    #                 # 'email_to' : self.crm_id.email_from, #default set recepient as company email in template
    #         })
    #         return {
    #                 'type': 'ir.actions.act_window',
    #                 'view_type': 'form',
    #                 'view_mode': 'form',
    #                 'res_model': 'mail.compose.message',
    #                 'views': [(compose_form_ids, 'form')],
    #                 'view_id': compose_form_ids,
    #                 'target': 'new',
    #                 'context': ctx,
    #         }


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    ''' for Resume tab in hr form... '''
    resume_details = fields.One2many('resume.details','job_id', string="Resume Details")
    document_ids = fields.One2many('ir.attachment','resume_emp_rel', string="Resume Details")
    pan_id = fields.Char(string="PAN No")
    user_id = fields.Many2one(comodel_name='res.users', related='resource_id.user_id', string="Related User")
    emp_street = fields.Char(related='user_id.partner_id.company_street', string="Street")
    emp_street2 = fields.Char(related='user_id.partner_id.company_street2', string="Street2")
    emp_street3 = fields.Char(related='user_id.partner_id.company_street3', string="Street3")
    emp_zip = fields.Char(related='user_id.partner_id.company_zip', string="Zip", change_default=True, size=5)
    emp_city = fields.Char(related='user_id.partner_id.company_city', string="City")
    emp_state_id = fields.Many2one(related='user_id.partner_id.company_state_id', string="State")
    emp_country_id = fields.Many2one(related='user_id.partner_id.company_country_id', string="Country")


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    resume_emp_rel = fields.Many2one('hr.employee')

class ResumeSales(models.Model):
    _name = 'resume.sales'
    _rec_name = 'name'

    # job_id = fields.Many2one('hr.employee')
    agreement_id = fields.Many2one('job.description',string="Agreement")
    name = fields.Char(string="Employee, Profile")
    profile = fields.Many2one('job.profile',string="Profile")
    resume = fields.Html(string='Resume')
    resume_post_sales = fields.Html(string='Resume Sales')
    sourcebl = fields.Binary(string='Class Description')
    datas_attachments = fields.Binary(string='Attachment',store=True)
    datas_attachments_fname = fields.Char(string="Attachment Name",store=True)
    employee_name = fields.Char(string="Employee")


    
    @api.multi
    def write(self, vals):
        for rec in self:
            atts = self.env['ir.attachment'].search([('res_model','=','resume.sales'),('res_id','=',self.id)])[0]
            atts.write({'datas':b64encode(str(vals.get('resume')))}) 
            vals.update({'datas_attachments':atts.datas,'datas_attachments_fname': atts.datas_fname,})            
            res = super(ResumeSales, self).write(vals)
            return res