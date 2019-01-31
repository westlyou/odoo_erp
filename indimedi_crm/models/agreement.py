# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import random
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import dateutil.relativedelta


class JobDescription(models.Model):
    _inherit = 'job.description'

    ''' New Lead gone to New stage by default in post sales.......... & set Stages at kanban in post state'''
    agreement_stage_id = fields.Many2one('agreement.stage', string="Agreement Stage", 
        track_visibility='onchange',
        group_expand='_read_group_stage_ids')
    stage_name = fields.Char(string="Name",related='agreement_stage_id.name')
    child_ids = fields.One2many(related='agreement_partner_id.child_ids', string='Subordinates')
    agreement_partner_id = fields.Many2one(related="crm_id.lead_partner_id", string="Contact")
    stage_hide = fields.Boolean(string="Stage Hide", default=False)
    interview_start_date = fields.Datetime(string="Interview Start Time")
    interview_stop_date = fields.Datetime(string="Interview Stop Time")
    execute_date = fields.Datetime('Execute Date', default=lambda self: fields.Datetime.now())
    agree_name = fields.Char('Agree Name')
    # resume_sales = fields.One2many('resume.sales','agreement_id',string="Resume")
    resume_many = fields.Many2one('resume.sales',string="Resumes")
    resume_post_sales = fields.Many2many(
        'resume.details',
        string='Resumes',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.')
    agreement_lead_owner = fields.Many2one('res.users',related='crm_id.user_id',string="Lead Owner")
    agreements_credentials = fields.One2many('credentials.agreement','agree',string="Credentials Agreement") 
    jd_post_timesheet_email = fields.Many2one('res.partner', string="Email Id")
    jd_post_timesheet_phone = fields.Char('Employee Phone')

    # duration = fields.Float(help="Duration in minutes and seconds.", default=0.5)

    @api.onchange('interview_start_date')
    def onchange_interview_start_date(self):
        for rec in self:
            rec.interview_stop_date = ((datetime.strptime(rec.interview_start_date, "%Y-%m-%d %H:%M:%S")) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.multi
    def _lead_hide_agreemnt(self):
        for res in self:
            #all agree condition in job description
            if all(res.crm_id.job_description_ids.mapped('agree')):
                res.crm_id.to_be_post_sales = True
            else:
                res.crm_id.to_be_post_sales = False

    # @api.onchange('agreement_stage_id')
    # def _onchange_agree_stage_id(self):
    #     print "_onchange_agree_stage_id"
    #     stage = str(self.agreement_stage_id.name)
    #     if stage == 'Resume Sent':
    #         if not self.resume_post_sales:
    #             raise ValidationError(_("Please Add the Resumes First"))

    # @api.onchange('resume_post_sales')
    # def _onchange_resume_post_sales(self):
    #     print ">>>>>>>>>>>LLLLLLLLLLLLL"
    #     for rec in self:
    #         for resume in rec.resume_post_sales:
    #             resume.employee_name = resume.job_id.name
    #             print ">>>>resume.employee_name >>>>>", resume.employee_name




    @api.multi
    def write(self, vals):
        #Employee Phone Number Format Logic
        if vals.get('jd_post_timesheet_phone'):
            track_list  = []
            for i in vals.get('jd_post_timesheet_phone'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Employee Phone Number.'))
                if len(track_list) > 12:
                    raise ValidationError(_('Not Valid Employee Phone Number.'))
            phone_str = vals['jd_post_timesheet_phone']
            phone_str = phone_str.replace('-', '').replace('-', '')
            phone = phone_str[0:3] + '-' + phone_str[3:6] + '-' + phone_str[6:10]
            vals['jd_post_timesheet_phone'] = phone

        stage = str(self.agreement_stage_id.name)
        if stage == 'Assignment Of Employee':
            raise ValidationError(_("Can't Change the stage" ))

        cr_details = {}
        for each in self.agreements_credentials:
            if each not in cr_details:
                cr_details.update({each:{'cred_timesheet':each.cred_agreement_post.id,'cred_description':each.cred_agreement_description_post}})
        

        #for hide tabs if stage is not ib Employee selected and Assignment Of Employee
        # if self.stage_hide:
        #     vals.update({'stage_hide':False})

        res = super(JobDescription, self).write(vals)
        stage_name = str(self.agreement_stage_id.name)

        #for prevent stages to be changed in backwards
        if stage == 'Employee Selected' and (stage_name == 'Interview Done' or stage_name == 'Interview Scheduled' or stage_name == 'Payment Received' or stage_name == 'New' or stage_name == 'Resume Sent'):
            raise ValidationError(_("Can't Change the stage in backwards" ))
        
        elif stage == 'Interview Done' and (stage_name == 'Interview Scheduled' or stage_name == 'Payment Received' or stage_name == 'New' or stage_name == 'Resume Sent'):
            raise ValidationError(_("Can't Change the stage in backwards" ))

        elif stage == 'Interview Scheduled' and (stage_name == 'Payment Received' or stage_name == 'New' or stage_name == 'Resume Sent'):
            raise ValidationError(_("Can't Change the stage in backwards" ))

        elif stage == 'Resume Sent' and  (stage_name == 'New' or stage_name == 'Payment Received'):
            raise ValidationError(_("Can't Change the stage in backwards" ))

        elif stage == 'Payment Received' and  stage_name == 'New':
            raise ValidationError(_("Can't Change the stage in backwards" ))


        if stage_name == 'Assignment Of Employee':
            project_obj = self.env['project.project']
            proj_name = str(self.jd_company) + '-' + str(self.name)
            project_id = project_obj.create({
                    'name': str(self.jd_company) + '-' + str(self.name),
                    'client_name': str(self.jd_company),
                    'user_id': self.jd_manager_id.id,
                    'partner_id': self.agreement_partner_id.id,
                    'sales_manager_id': self.env.user.id,
                    'jd_ea_working_id': self.jd_ea_working_id.id,
                    'jd_us_name_id': self.jd_us_name_id.id,
                    'project_general_manager':self.agreement_general_manager.id,
                    'timesheet_email_id': self.jd_post_timesheet_email.id,
                    'timesheet_phone': self.jd_post_timesheet_phone,
                    'invoicing_type_id': self.jd_invoicing_post.id,
                    'invoice_start_date': self.start_date_billing,
                    'hour_selection': self.hour_selection,
                    'rate_per_hour': self.rate_per_hour_jd,
                    'total_rate': self.total_rate,
                    'client_email': str(self.jd_email),
                    'date_of_join': self.start_date_billing,
                })
            
            bill_obj = self.env['billing.history']
            
            bill_vals = {
                    'project_id': project_id.id,
                    'invoice_start_date': project_id.invoice_start_date,
                    'rate_per_hour': project_id.rate_per_hour,
                    'total_rate': project_id.total_rate,
                    'invoicing_type_id': project_id.invoicing_type_id.id,
                    'hour_selection': project_id.hour_selection,
                    'user_id': self.env.user.id,
                    }
            
            bill_id = bill_obj.create(bill_vals)
            
            task_obj = self.env['project.task'].create({
                    'name': str(self.jd_company) + '-' + str(self.name),
                    'project_id': self.env['project.project'].search([('name','=',proj_name)]).id,
                    'email_id':self.jd_email,
                    'phone':self.jd_phone,
                    'profile_id':self.job_profile_id.name,
                    'credential_ts': [(0,0,cr_details[each])for each in cr_details],
                })

        if stage_name == 'Assignment Of Employee':
            if self.jd_ea_working_id and self.jd_us_name_id and self.jd_manager_id.id:
                pass
            else:
                raise ValidationError(_('Please Fill All Require fields'))

        else:
            if self.jd_ea_working_id and self.jd_us_name_id and self.jd_manager_id.id and stage == 'Employee Selected':
                name_stage = self.env['agreement.stage'].search([('name','=','Assignment Of Employee')])
                self.agreement_stage_id = name_stage.id

 
        if not self.stage_hide:
            if stage_name == 'Interview Done':
                self.stage_hide = True

            elif self.agreement_stage_id.name == 'Employee Selected':
                self.stage_hide = True

        # Resume Validation before 'Resume Send' Stage
        if stage_name == 'Resume Sent':
            for resume in self:
                if resume.resume_post_sales:
                    pass
                else:
                    raise ValidationError(_("Please Add the Resumes First"))

        #Interview Scheduled Stage Validation
        if stage_name == 'Interview Scheduled':
            if not self.interview_start_date:
                raise ValidationError(_("Please Add Interview Date First"))

        # Interview Auto Stage Change and Date Validation
        if stage_name == 'New' or stage_name == 'Resume Sent' or stage_name == 'Payment Received':
            if self.interview_start_date:
                current_datetime = datetime.now()
                if datetime.strptime(self.interview_start_date, "%Y-%m-%d %H:%M:%S") < current_datetime:
                    raise ValidationError(_("You can not Scheduled Interview in Past, Please Enter the Valid Date."))
                else:
                    interview_stage = self.env['agreement.stage'].search([('name','=','Interview Scheduled')])
                    self.update({
                                'agreement_stage_id' : interview_stage.id
                            })

        if self.agree and self.crm_id.stage_id.name != 'Assign to General Manager':
            c_name = self.jd_company
            comp_name = self.env['res.partner'].search([('name','=',c_name)])
            comp_name.write({'pre_sale_contacts':False,'post_sale_contacts':True})

            
            # if self.crm_id.stage_id.name != 'Agreement Signed':
            #     self.crm_id.stage_id = sign_stage.id
            # print ">>>LLL >>>>>>", self.crm_id.stage_id.name


            for partner in comp_name:
                if partner.is_company: 
                    for i in partner.child_ids:
                        if i.pre_sale_contacts:
                            i.pre_sale_contacts = False
                        if not i.post_sale_contacts:
                            i.post_sale_contacts = True




        # self._lead_hide_agreemnt()
        return res


    @api.model
    def create(self, vals):
        new_stage_id = self.env['agreement.stage'].search([],order="id",limit=1)
        vals.update({
            'agreement_stage_id' : new_stage_id.id
        })
        res = super(JobDescription, self).create(vals)

        random_var = ''.join(random.choice('0123456789') for i in range(3))
        seq = self.env['ir.sequence'].next_by_code('job.description').split('/')
        if vals.get('hiring_model','') == 'permanent':
            seq.insert(1,"P")
        else:
            seq.insert(1,"T")
        del seq[4]
        seq = '/'.join(seq)
        seq += '/' + random_var
        res.name = seq
        res.jd_company = self.env['crm.lead'].browse(vals['crm_id']).name
        res.jd_email = self.env['crm.lead'].browse(vals['crm_id']).email_from
        res.jd_phone = self.env['crm.lead'].browse(vals['crm_id']).phone
        res.jd_street = self.env['crm.lead'].browse(vals['crm_id']).c_street
        res.jd_street2 = self.env['crm.lead'].browse(vals['crm_id']).c_street2
        res.jd_street3 = self.env['crm.lead'].browse(vals['crm_id']).c_street3
        res.jd_zip = self.env['crm.lead'].browse(vals['crm_id']).c_zip
        res.jd_city = self.env['crm.lead'].browse(vals['crm_id']).c_city
        res.jd_state_id = self.env['crm.lead'].browse(vals['crm_id']).c_state_id
        res.jd_country_id = self.env['crm.lead'].browse(vals['crm_id']).c_country_id
        res.jd_twitter_id = self.env['crm.lead'].browse(vals['crm_id']).lead_twitter
        res.jd_fax = self.env['crm.lead'].browse(vals['crm_id']).lead_fax
        res.jd_website = self.env['crm.lead'].browse(vals['crm_id']).lead_website

        #Pre to Post customer Transfer
        if res.agree:
            # import pdb
            # pdb.set_trace()
            c_name = res.jd_company
            comp_name = self.env['res.partner'].search([('name','=',c_name)])
            comp_name.write({'pre_sale_contacts':False,'post_sale_contacts':True})
            # comp_name = self.env['res.partner'].search([('name','=',c_name)])
            

            # stage = self.env['crm.stage'].search([('name', '=', 'Agreement Signed')], limit=1)
            # stage_name = str(res.crm_id.stage_id.name)
            # # print ">>>>>>>AGREE Create>>>>",stage_name
            # if stage_name != 'Assign to General Manager' and stage_name != 'Agreement Signed':
            #     # res.crm_id.transfer = True
            #     res.crm_id.stage_id = stage.id
            #     # print ">>>>>>>AGREE crea>>>>",self.crm_id.stage_id.name

                


            for partner in comp_name:
                if partner.is_company: 
                    for i in partner.child_ids:
                        if i.pre_sale_contacts:
                            i.pre_sale_contacts = False
                        if not i.post_sale_contacts:
                            i.post_sale_contacts = True

            return res
        # res._lead_hide_agreemnt()
        else:
            return res


    @api.multi
    def send_resumes_post_sales(self):
        temp_m = self.resume_post_sales.ids
        resumes = self.env['ir.attachment'].search([('res_model','=','resume.sales'),('res_id','in',temp_m)])

        ir_model_data = self.env['ir.model.data']
        
        if self.jd_email:
            pass
        else:
            raise ValidationError(_('Please fill email id of company whome you want to send.'))

        for resume in self:
            if resume.resume_post_sales:
                pass
            else:
                raise ValidationError(_("Please Add the Resumes First"))


        user_name = self.env.user.name
        template = self.env.ref('indimedi_crm.email_resume_post_sales')
        user_email_id = self.env.user.email
        ctx = dict(email_from= str(user_email_id),
                    email_to= self.jd_email,
                    user_name=user_name,
                    reply=str(user_email_id))
        # self.env['mail.template'].browse(template.id).with_context(ctx).send_mail(self.id)


        # template = self.env['mail.template'].create({'model_id':self.env['ir.model'].search([('model', '=', 'resume.details')], limit=1).id,'name':str(self.name),'body_html':self.resume,})               
        template_id = template.id
        compose_form_ids = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        # ctx = dict()
        ctx.update({
                'default_model': 'job.description',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'default_attachment_ids':[(6,0,resumes.ids)],
                'default_mail_partner_id':self.agreement_partner_id.id,
                'default_mail_user_general_manager':self.agreement_general_manager.id,
                'default_mail_lead_owner':self.agreement_lead_owner.id,
                'mark_so_as_sent': True,
                'custom_layout': "email_resume_post_sales",
                # 'email_to' : self.crm_id.email_from, #default set recepient as company email in template
        })
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_ids, 'form')],
                'view_id': compose_form_ids,
                'target': 'new',
                'context': ctx,
        }


class AgreementStage(models.Model):
    _name = 'agreement.stage'

    name = fields.Char(string="Name")
    default = fields.Integer("Run")
    last_stage = fields.Boolean('Last Stage')

    @api.model
    def create(self, vals):
        vals.update({
            'default' : 10
        })
        return super(AgreementStage, self).create(vals)



class CredentialsAgreement(models.Model):
    _name = 'credentials.agreement'

    # name = fields.Char(string='Name')
    cred_agreement_post = fields.Many2one('credentials.task',string="Name")
    cred_agreement_description_post = fields.Text(name="Description")
    agree = fields.Many2one('job.description',string="Jobs")