# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

import time
import random

# PERMANENT_HOURS = [('40', '40 Hours'), ('160', '160 Hours'), ('180', '180 Hours'), ('200', '200 Hours')]
# TEMPORARY_HOURS = [('10', '10 Hours'), ('20', '20 Hours'), ('30', '30 Hours'), ('80', '80 Hours'), ('90', '90 Hours'), ('100', '100 Hours'), ('40_20', '40-20 Hours'), ('20_10', '20-10 Hours')]
PERMANENT_HOURS = [('10', '10 Hours'), ('20', '20 Hours'), ('30', '30 Hours'), ('40', '40 Hours'),('80', '80 Hours'), ('90', '90 Hours'), ('100', '100 Hours'), ('160', '160 Hours'), ('180', '180 Hours'), ('200', '200 Hours'), ('40_20', '40-20 Hours'), ('20_10', '20-10 Hours')]
TEMPORARY_HOURS = [('20', '20 Hours'), ('40', '40 Hours')]

class CrmLead(models.Model):
    _inherit = "crm.lead"

    def _compute_lead_activity_count(self):
        for lead in self:
            lead.lead_activity_count = len(lead.custom_activity_ids)


    @api.model
    def _get_default_allocation(self):
        allocation = self.env['crm.allocation'].search([('name', '=', 'RS')])
        return allocation

    lead_activity_count = fields.Integer(compute="_compute_lead_activity_count", string="Tasks")
    lead_partner_id = fields.Many2one('res.partner', string="Partner")
    custom_activity_ids = fields.One2many('custom.activity','crm_custom_id', string="Activities")
    #Contact Info Tab Fields
    job_description_ids = fields.One2many('job.description','crm_id', string="Agreement & Job Description")
    child_ids = fields.One2many(related='lead_partner_id.child_ids', string='Subordinates')
    # Fields for Company address
    c_street = fields.Char('Street', size=5)
    c_street2 = fields.Char('Street2')
    c_street3 = fields.Char('Street3')
    c_zip = fields.Char('Zip', change_default=True, size=5)
    c_city = fields.Char('City')
    c_state_id = fields.Many2one("res.country.state", string='State')
    c_country_id = fields.Many2one('res.country', string='Country')
    lead_fax = fields.Char(string="Fax")
    lead_website = fields.Char(string="Website")
    lead_twitter = fields.Char(string="Twitter")
    lead_name = fields.Char(string='Name')
    industry_served = fields.Text(string='Industry Served')
    number_of_staff = fields.Selection([('sole propietor','SOLE PROPRIETOR'),('1 to 3','1 to 3'),('4 to 10','4 to 10'),('10 to 20','10 to 20'),('20 +','20+')], string="No. of staff")
    service_provided = fields.Many2many('service.provided','service_provided_id','crm_id', string="Service Provided")
    category = fields.Selection([('accounting','ACCOUNTING FIRM'),('business','Business'),('government','Government/Colleges/Others')], string="Category")
    firm = fields.Selection([('cpa','CPA FIRM'),('ea','EA FIRM'),('tax','TAX PRACTICE'),('back','BACK OFFICE FIRM'),('financial','FINANCIAL PLANNING FIRM')], string="Firm")
    service_provided = fields.Many2many('service.provided', 'service_provided_id', 'crm_id', string="Service Provided")
    #Fields for many2many field allocation relation with tabs...
    allocation = fields.Many2many('crm.allocation', 'crm_allocation_id', 'crm_id', string="Allocation", default=_get_default_allocation)
    allocation_first = fields.Char("Value first")
    allocation_second = fields.Char("Value second")
    allocation_third = fields.Char("Value third")
    allocation_d_and_a = fields.Boolean("D&A", default=False)
    allocation_wfc = fields.Boolean("WFC", default=False)
    allocation_rs = fields.Boolean("RS", default=False)
    parent_id = fields.Many2one("res.partner", string='Parent')
    #field for lead will disappear from lead after agreement
    to_be_post_sales = fields.Boolean('Convert to post Sales', default=False)
    general_manager = fields.Many2one('res.users', string="General Manager")
    # is_gm = fields.Boolean(string="Custom Stage", default=False, compute="_onchange_stage_id")
    meeting_ids = fields.One2many('calendar.event', 'opportunity_id', stirng="Meetings")
    client_priority = fields.Selection([('high', 'High'),
                                        ('medium', 'Medium'),
                                        ('low', 'Low')], string="Priority")
    client_firm = fields.Selection([('big', 'Big Firm'),
                                    ('normal', 'Normal Firm'),
                                    ('small', 'Small Firm')], string="Client Firm")
    subsidiary_id = fields.Many2one('subsidiary.master', string="Billing Company")
    
    @api.multi
    def action_schedule_meeting(self):
        """ Open meeting's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view
            and set default meeting set to scheduling.... 
        """
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        action['context'] = {
            'search_default_opportunity_id': self.id if self.type == 'opportunity' else False,
            'default_opportunity_id': self.id if self.type == 'opportunity' else False,
            'default_partner_id': self.partner_id.id,
            'default_partner_ids': partner_ids,
            'default_team_id': self.team_id.id,
            'default_name': self.name,
            'default_cal_street': self.c_street,
            'default_cal_street2': self.c_street2,
            'default_cal_street3': self.c_street3,
            'default_cal_zip': self.c_zip,
            'default_cal_city': self.c_city,
            'default_cal_state_id': self.c_state_id.id,
            'default_cal_country_id': self.c_country_id.id,
            'default_shedular' : 'meeting',
        }
        return action

    @api.multi
    def action_schedule_calling(self):
        """ Open Call's calendar view to schedule meeting on current opportunity.
            :return dict: dictionary value for created Meeting view and set schduling
            to calling by default.
        """
        self.ensure_one()
        action = self.env.ref('calendar.action_calendar_event').read()[0]
        partner_ids = self.env.user.partner_id.ids
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        action['context'] = {
            'search_default_opportunity_id': self.id if self.type == 'opportunity' else False,
            'default_opportunity_id': self.id if self.type == 'opportunity' else False,
            'default_partner_id': self.partner_id.id,
            'default_partner_ids': partner_ids,
            'default_team_id': self.team_id.id,
            'default_name': self.name,
            'default_cal_street': self.c_street,
            'default_cal_street2': self.c_street2,
            'default_cal_street3': self.c_street3,
            'default_cal_zip': self.c_zip,
            'default_cal_city': self.c_city,
            'default_cal_state_id': self.c_state_id.id,
            'default_cal_country_id': self.c_country_id.id,
            'default_shedular' : 'call',
        }
        return action   

    @api.onchange('allocation')
    def char_val(self):
        ''' for Many2many field allocation relation woth tabs'''

        self.allocation_d_and_a = False
        self.allocation_wfc = False    
        self.allocation_rs = False
        if(len(self.allocation)==0):
            self.allocation_first=False
        if self.allocation:
            count=0
            for rec in self.allocation:
                if(len(self.allocation) > 0):
                    count+=1
                    if(count==1):
                        self.allocation_first=rec.name
                        if self.allocation_first == 'D&A':
                            self.allocation_d_and_a = True
                        if self.allocation_first == 'WFC':
                            self.allocation_wfc = True
                        if self.allocation_first == 'RS':
                            self.allocation_rs = True
                        self.allocation_second=False
                    if(count==2):
                        self.allocation_second=rec.name
                        if self.allocation_second == 'D&A':
                            self.allocation_d_and_a = True
                        if self.allocation_second == 'WFC':
                            self.allocation_wfc = True
                        if self.allocation_second == 'RS':
                            self.allocation_rs = True
                        self.allocation_third=False

                    if(count==3):
                        self.allocation_third=rec.name
                        if self.allocation_third == 'D&A':
                            self.allocation_d_and_a = True
                        if self.allocation_third == 'WFC':
                            self.allocation_wfc = True
                        if self.allocation_third == 'RS':
                            self.allocation_rs = True

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone:
            self.phone = self.phone[0:3] + '-' + self.phone[3:6] + '-' + self.phone[6:10]

    @api.constrains('stage_id')
    def check_stages(self):
        if self._context.get('system', None):
            return
        stage_assigned = self.env['crm.stage'].search([('name', '=', 'Assign to General Manager')], limit=1)
        state_sign= self.env['crm.stage'].search([('name', '=', 'Agreement Signed')], limit=1)
        have_manager = agreed = False
        domain = ['|', ('active', '=', False), ('active', '=', True), ('crm_id', '=', self.id)]
        for line in self.job_description_ids.search(domain):
            if line.agreement_general_manager:
                have_manager = True
            if line.agree:
                agreed = True
        if not have_manager and stage_assigned.id == self.stage_id.id:
            raise ValidationError(_("Please Add General Manager First in the Agreement." ))
        if not agreed and state_sign.id == self.stage_id.id:
            raise ValidationError(_("Please Agree the Agreement First." ))

    @api.multi
    def compute_lead_stage(self):
#         print "1111>>>>>>>>>>>>>>"
        stage_assigned = self.env['crm.stage'].search([('name', '=', 'Assign to General Manager')], limit=1)
        state_sign= self.env['crm.stage'].search([('name', '=', 'Agreement Signed')], limit=1)
        have_manager = agreed = False
#         print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        domain = ['|', ('active', '=', False), ('active', '=', True), ('crm_id', '=', self.id)]
        for line in self.job_description_ids.search(domain):
            if line.agreement_general_manager:
                have_manager = True
            if line.agree:
                agreed = True
#         print ">>>>>>>>>>>????????????", agreed and have_manager and stage_assigned.id != self.stage_id.id
        if agreed and have_manager and stage_assigned.id != self.stage_id.id:
            self.env.cr.execute(_("""update crm_lead set stage_id=%s where id=%s"""%(stage_assigned.id, self.id)))
        elif not have_manager and agreed and state_sign.id != self.stage_id.id:
            self.env.cr.execute(_("""update crm_lead set stage_id=%s where id=%s"""%(state_sign.id, self.id)))

    @api.multi
    def write(self, vals):
        stage_before_name = str(self.stage_id.name)
        res = super(CrmLead, self).write(vals)
        stage_name = str(self.stage_id.name)

        if vals.get('job_description_ids'):
#             print "write gm>>>>>>>>>>>>>>"
            self.compute_lead_stage()

        if stage_before_name == 'Assign to General Manager' and stage_name !='Assign to General Manager':
            raise ValidationError(_("Agreement is Signed and General Manager Assigned, You Can't Change the stage now." ))

        return res


class JobDescription(models.Model):
    _name = "job.description"
    _inherit = ['mail.thread']

    @api.depends('stage_id')
    def _onchange_stage_id(self):
        for stage in self:
            stage.stage_id = stage.crm_id.stage_id
            if stage.stage_id.filtered(lambda cat: cat.name.lower() == 'hot'):
                stage.is_gm = True

    @api.multi
    def toggle_active(self):
#         print "toggle_active<>>>>>>>>>>>>>>>>><<<<<<"
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active

    # @api.onchange('agree')
    # def _onchange_agree_active(self):
    #     if self.agree and self.agreement_general_manager:
    #         self.active = False
    #     else:
    #         self.active = True

    name = fields.Char(string='Ref #', size=128, copy=False)
    active = fields.Boolean(default=True, help="The active field allows you to hide the Agreement without removing it.")
    agree = fields.Boolean("Agree",default=False)
    crm_id = fields.Many2one('crm.lead', string="Lead")
    stage_id = fields.Many2one('crm.stage')
    #Job Description Tab Fields
    job_profile_id = fields.Many2one('job.profile', string="Profile")
    experience_id = fields.Many2one('job.experience', string="Experience")
    nature_experience_ids = fields.Many2many('nature.experience','crm_job_nature_exp_rel','nature_experience_id','crm_id', string="Nature of Experience")
    task_tobe_done = fields.Char(string="Task to be Done")
    s_accounting_ids = fields.Many2many('accounting.software','job_acc_software_rel','s_accounting_id','crm_id', string="Accounting Software")
    s_tax_id_ids = fields.Many2many('tax.software','job_tax_software_rel','s_tax_id_id','crm_id', string="Tax Software")
    hiring_model = fields.Selection([('permanent','Permanent'),('temporary','Temporary'),('On Demand', 'On Demand')],default='permanent', string="Hiring Model")
    hiring_option = fields.Selection([('full_time','Full Time'),('part_time','Part Time')], string="Hiring Option")
    # full_time_hr = fields.Selection([('40','40 Hours a Week'),('160','160 Hours a Week'),('180','180 Hours a Week'),('200','200 Hours a Week')], default='40', string="Full Time Hours")
    # part_time_hr = fields.Selection([('10','10 Hours a Week'),('20','20 Hours a Week'),('30','30 Hours a Week'),('80','80 Hours a Week'),('90','90 Hours a Week'),('100','100 Hours a Week'),('40-20','40-20 Hours a Week'),('20-10','20-10 Hours a Week')], string="Part Time Hours")

    hour_selection = fields.Selection([('10','10 Hours'),('20','20 Hours'),('30','30 Hours'),('40','40 Hours'),('80','80 Hours'),('90','90 Hours'),('100','100 Hours'),('40_20','40-20 Hours'),('20_10','20-10 Hours'),('160','160 Hours'),('180','180 Hours'),('200','200 Hours')], string="Working Hours")

    permanent_hour_selection = fields.Selection(PERMANENT_HOURS, string="Working Hours")
    temporary_hour_selection = fields.Selection(TEMPORARY_HOURS, string="Working Hours")
    permanent_hour_jd = fields.Selection(related='permanent_hour_selection', string="Minimum Hours")
    temporary_hour_jd = fields.Selection(related='temporary_hour_selection', string="Minimum Hours")
    start_date_billing = fields.Date(string="Start Date")
    general_manager = fields.Many2one('res.users', string="General Manager", compute="_onchange_stage_id", readonly=False, store=True)
    is_gm = fields.Boolean(string="Custom Stage", default=False, compute="_onchange_stage_id")
    agreement_general_manager = fields.Many2one('res.users', string="General Manager",store=True)
 

    ''' fields for agreement at post sales form '''
    # jd_street = fields.Char('Address 1')
    # jd_street2 = fields.Char('Address 2')
    # jd_zip = fields.Char('P.O. BOX', change_default=True,size=5)
    # jd_city = fields.Char('City')
    # jd_state_id = fields.Many2one("res.country.state", string='State')
    # jd_country_id = fields.Many2one('res.country', string='Country')
    jd_street = fields.Char('Street')
    jd_street2 = fields.Char('Street2')
    jd_street3 = fields.Char('Street3')
    jd_zip = fields.Char('P.O. BOX', change_default=True, size=5)
    jd_city = fields.Char('City')
    jd_state_id = fields.Many2one("res.country.state", string='State')
    jd_country_id = fields.Many2one('res.country', string='Country')

    jd_website = fields.Char(string="Website")
    jd_email = fields.Char(string="Email id")
    jd_google_page = fields.Char(string="Google Business Page")
    jd_facebook_page = fields.Char(string="Facebook Page")
    jd_twitter_id = fields.Char(string="Twitter Id")
    jd_assigned_to = fields.Many2one('hr.employee', string="Assigned To")
    jd_company = fields.Char(string="Company Name")
    jd_phone = fields.Char('Phone')
    jd_fax = fields.Char('Fax')
    jd_feedback_response = fields.Selection([('5','5-Excellent'),('4','4-Very Good'),('3','3-Good'),('2','2-Fair'),('1','1-Poor')], string="Feedback Response")
    jd_feedback_work_product = fields.Selection([('5','5-Excellent'),('4','4-Very Good'),('3','3-Good'),('2','2-Fair'),('1','1-Poor')], string="Feedback Work Product/Quality")
    jd_feedback_work_flow = fields.Selection([('5','5-Excellent'),('4','4-Very Good'),('3','3-Good'),('2','2-Fair'),('1','1-Poor')], string="Feedback Work Flow Management")
    jd_feedback_response_remark = fields.Text(string="Remark")
    jd_feedback_work_product_remark = fields.Text(string="Remark")
    jd_feedback_work_flow_remark = fields.Text(string="Remark")
    types = fields.Many2one('client.credentials',string="Types")
    jd_call_overall_remarks = fields.Text(string="Call Overall Remarks")
    client_credential_email_id = fields.Char(string="Email Id", placeholder="mymail@mail.com")
    client_credential_password = fields.Char(string="Password")
    remote_id = fields.Char(string="Email Id", placeholder="mymail@mail.com")
    remote_password = fields.Char(string="Password")
    as_id = fields.Char(string="Email Id", placeholder="mymail@mail.com")
    as_password = fields.Char(string="Password")
    tax_software_id = fields.Char(string="Email Id", placeholder="mymail@mail.com")
    tax_software_password = fields.Char(string="Password")
    jd_minimum_hours = fields.Integer(string="Minimum Hours")
    jd_invoicing = fields.Many2one('job.invoicing',string="Invoicing")
    jd_invoicing_post = fields.Many2one(related='jd_invoicing', string="Invoicing", readonly="1")
    jd_invoicing_bill = fields.Many2one(related='jd_invoicing', string="Invoicing")
    jd_ea_working_id = fields.Many2one('res.users',string="EA Working")
    jd_us_name_id = fields.Many2one('res.users',string="US Name")
    jd_manager_id = fields.Many2one('res.users',string="Manager")
    # This is Removed as per the client said now- 4th sept
    jd_entigrity_email = fields.Char(string="Email Id",placeholder="employee@employee.com")
    #####################################
    jd_entigrity_password = fields.Char(string="Password")
    jd_skype_email = fields.Char(string="Skype Id")
    jd_skype_password = fields.Char(string="Password")
    jd_description = fields.Text(string="Description")

    @api.onchange('agree', 'agreement_general_manager')
    def set_active(self):
        if self.agree and self.agreement_general_manager:
            self.active = False
        else:
            self.active = True

    @api.onchange('hiring_model')
    def _onchange_hiring_model(self):
        if self.hiring_model == 'permanent':
            self.hour_selection = self.temporary_hour_selection = False
        elif self.hiring_model == 'temporary':
            self.hour_selection = self.permanent_hour_selection = False

    @api.onchange('permanent_hour_selection', 'temporary_hour_selection')
    def _onchange_hour_selection(self):
        if self.permanent_hour_selection:
            self.hour_selection = self.permanent_hour_selection
        elif self.temporary_hour_selection:
            self.hour_selection = self.temporary_hour_selection


    # @api.onchange('jd_us_name_id')
    # def _onchange_credentials_email(self):
    #     self.jd_entigrity_email = self.jd_us_name_id.email
    #     self.jd_skype_email = self.jd_us_name_id.email

    hiring_period = fields.Selection([('week','Week'),('month','Month')], string="Working Period",default='week')
    rate_per_hour = fields.Float(string="Rate Per Hour")
    rate_per_hour_jd = fields.Float(related='rate_per_hour', string="Rate Per Hour")
    rate_per_hour_inv = fields.Float(related='rate_per_hour', string="Rate Per Hour")
    writing_skill = fields.Selection([('average','Average'),('good','Good'),('excellent','Excellent')], string="Writing Skill :")
    speaking_skill = fields.Selection([('average','Average'),('good','Good'),('excellent','Excellent')], string="Speaking Skill :")
    comm_medium_ids = fields.Many2many('comm.medium','job_comm_rel','comm_medium_id','crm_id', string="Communication Medium")
    soft_access = fields.Selection([('remote','Remote'),('cloud','Cloud'),('local','Local')], string="Software Access")
    soft_remote_id = fields.Many2one('software.remote', string="Software Remote Access")
    soft_cloud_id = fields.Many2one('software.cloud', string="Software Cloud Access")
    soft_local_id = fields.Many2one('software.local', string="Software Local Access")
    doc_access = fields.Selection([('remote','Remote'),('cloud','Cloud'),('sharing','Sharing')], string="Document Access")
    doc_remote_id = fields.Many2one('document.remote', string="Document Remote Access")
    doc_cloud_id = fields.Many2one('document.cloud', string="Document Cloud Access")
    doc_sharing_id = fields.Many2one('document.sharing', string="Document Sharing Access")
    time_from = fields.Date(string="From")
    time_to = fields.Date(string="To")
    remark = fields.Char(string="Remark")
    # reporting = fields.Selection([('direct_to_owner_or_partner','Direct To Owner Or Partner'),('staff','Staff'),('both','Both')], string="Reporting")
    reporting_id = fields.Many2one('res.partner', string="Reporting", default=False)
    tentative_date = fields.Date(string="Tentative Start Date")
    # timezone = fields.Selection([('est','EST'),('mst','MST'),('cst','CST'),('pst','PST')], string="Working Time Zone")
    timezone_id = fields.Many2one('working.timezone', string="Working Timezone")
    from_timezone_id = fields.Many2one('from.timezone', string="Time From")
    to_timezone_id = fields.Many2one('to.timezone', string="Time From")
    #Agreement Tab Fields
    multi_agreement = fields.Selection([('active','Active'),('inactive','Inactive')], default='active', string="Multiple Agreement / Mapping")
    generation_date = fields.Date(string="Date of Generation", default=datetime.today())
    agreement_rate = fields.Integer(string="Per Hour Rate")
    hours_week = fields.Integer(string="No. Of Hours Per Week/Month")
    total_rate = fields.Float('Total Rate', compute="_get_total_rate", digits=(16,2), store=True)
    jd_mail_from = fields.Char('Mail From')
    ip_add_of_user = fields.Char('IP') #Field for fetch ip of user who agreed agreement 

    @api.multi
    def action_agreement_send(self):
            '''
            for send agreement, here default set tempate permenent 
            if hiring model permenent selected and it set temporary if temporary selected. 
            {{ DESCRIPTION }}
            '''
            # import pdb
            # pdb.set_trace()
            self.ensure_one()
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = self.env.ref('indimedi_crm.email_template_agreement_crm_signup')
#                 if self.hiring_model == 'permanent' and self.permanent_hour_selection in ['40_20','20_10'] :
#                     template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm_signup')[1]   
#                 elif self.hiring_model == 'permanent':
#                     template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm')[1]
#                 elif self.hiring_model == 'temporary':
#                     template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm_second')[1]
#                 else:
#                     template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False

            # self.resume_details = [(6, 0 , [y for y in (self.env['ir.attachment'].search([('res_model','=','resume.details')]).ids)])]
            us_email_id = str(self.env.user.email)
            user_name = str(self.env.user.name)
            ctx = dict(email_from= us_email_id,
                        user_name= user_name,
                        default_attachment_ids=[(6,0, [20554])]) #20554 server
            
            
            
            
             
            ctx.update({
                    'default_model': 'job.description',
                    'default_res_id': self.ids[0],
#                     'default_use_template': bool(template_id),
#                     'default_template_id': template_id,
#                     'default_composition_mode': 'comment',
                    'mark_so_as_sent': True,
                    'custom_layout': "email_template_agreement_crm",
                    'email_to' : self.crm_id.email_from, #default set recepient as company email in template
            })

            email_vals = template_id.with_context(ctx).sudo().generate_email(self.id)
            email_vals['attachment_ids'] = [(6,0, [20554])]
            mail_id = self.env['mail.mail'].sudo().create(email_vals)
            mail_id.send()
            
            view_id = self.env.ref('indimedi_crm.popup_massage_wizard')
            return {
                    'name': "Notification",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'popup.massage',
                    'view_id': view_id.id,
                    'target': 'new',
                    'context': {'default_name': "Email successfully sent"},
                    
                }
#             return {
#                     'type': 'ir.actions.act_window',
#                     'view_type': 'form',
#                     'view_mode': 'form',
#                     'res_model': 'mail.compose.message',
#                     'views': [(compose_form_id, 'form')],
#                     'view_id': compose_form_id,
#                     'target': 'new',
#                     'context': ctx,
#             }

    @api.multi
    def action_resume_send(self):
            '''
            for send agreement, here default set tempate permenent 
            if hiring model permenent selected and it set temporary if temporary selected. 
            {{ DESCRIPTION }}
            '''
            self.ensure_one()
            # ir_model_data = self.env['ir.model.data']
            # template = self.['mail.template'].create({'body_html':parth})
            try:
                if self.hiring_model == 'permanent' and self.permanent_hour_selection in ['40_20','20_10'] :
                    template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm_part_time')[1]   
                elif self.hiring_model == 'permanent':
                    template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm')[1]
                elif self.hiring_model == 'temporary':
                    template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm_second')[1]
                else:
                    template_id = ir_model_data.get_object_reference('indimedi_crm', 'email_template_agreement_crm')[1]
            except ValueError:
                    template_id = False
            try:
                    compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                    compose_form_id = False
            us_email_id = str(self.env.user.email)
            user_name = str(self.env.user.name)
            ctx = dict(email_from= us_email_id,
                        user_name= user_name)
            ctx.update({
                    'default_model': 'job.description',
                    'default_res_id': self.ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                    'mark_so_as_sent': True,
                    'custom_layout': "email_template_agreement_crm",
                    'email_to' : self.crm_id.email_from, #default set recepient as company email in template
            })
            return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
            }



    @api.multi
    def send_mail_templates(self):

        if self.agree:
            # Find the e-mail template
            template = self.env.ref('indimedi_crm.email_template_agreement_submitted')

            ctx = dict(
                email_to= self.env.user.email)
            self.env['mail.template'].browse(
                template.id).with_context(ctx).send_mail(self.id)

            if self.jd_mail_from:
                ctx = dict(
                    email_from=self.env.user.email,
                    email_to= self.jd_mail_from)
                self.env['mail.template'].browse(
                    template.id).with_context(ctx).send_mail(self.id)


    @api.onchange('tentative_date')
    def onchange_tentative_date(self):
        for date in self:
            if date.hour_selection == '40_20':
                date.time_from = date.tentative_date
            if date.hour_selection == '20_10':
                date.time_from = date.tentative_date

    @api.onchange('hour_selection')
    def onchange_hour_selection(self):
        for time in self:
            time.hiring_option = False
            if time.hour_selection == '40' or time.hour_selection == '160' or time.hour_selection == '180' or time.hour_selection == '200':
                time.hiring_option = 'full_time'
            else:
                time.hiring_option = 'part_time'
            # if time.hour_selection == '40-20' or time.hour_selection == '20-10':

    @api.depends('hour_selection','rate_per_hour')
    def _get_total_rate(self):
        for rate in self:
            if rate.hour_selection == '40_20':
                rate.total_rate = round((float(rate.rate_per_hour)) * 60)
            elif rate.hour_selection == '20_10':
                rate.total_rate = round((float(rate.rate_per_hour)) * 30)
            elif rate.rate_per_hour and rate.hour_selection:
                rate.total_rate = round((float(rate.rate_per_hour)) * (float(rate.hour_selection)))
            else:
                pass

    # Do not Touch Here !!!
    @api.onchange('job_profile_id')
    @api.multi
    def _onchnahge_job_profile_id(self):
        for data in self:
            # print ">>>>>data.crm_id.child_ids >>>>>>>>>>", data.crm_id.child_ids
            # print "?>>>>>>>>>>>>>>>>....", [i.id for i in data.crm_id.child_ids]
            return {'domain':{'reporting_id':[('id','in',[i.id for i in data.crm_id.child_ids])]}}


#Activity Tab Fields
class CustomActivity(models.Model):
    _name = "custom.activity"

    crm_custom_id = fields.Many2one('crm.lead', string="Lead Name")
    name = fields.Char(related="crm_custom_id.name", string="Lead Name")
    mark_done = fields.Boolean(string="Mark Done")
    crm_activity_id = fields.Many2one('lead.custom.activity', string="Activity")
    assigned_to_act = fields.Many2one('res.users', string="Assigned to", default=lambda self: self.env.user)
    custom_date_action = fields.Datetime(string="Activity Date", index=True)
    custom_title_action = fields.Char(string="Activity Summary")
    custom_date_deadline = fields.Datetime(string="Due Date", help="Estimate of the date on which the activity will be won.")
    description = fields.Text(string="Description")
    team_id = fields.Many2one('crm.team', string='Sales Team')
    state = fields.Selection([('pending', 'Pending'),('done','Done'),('cancel', 'Cancel')], string="State",
                             default='pending', copy=False)

    @api.multi
    def mark_as_done(self):
        self.state = 'done'
        self.mark_done = True
    
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

class WorkingTimezone(models.Model):
    _name = "working.timezone"

    name = fields.Char(string="Name")


class FromTimezone(models.Model):
    _name = "from.timezone"

    name = fields.Char(string="Name")


class ToTimezone(models.Model):
    _name = "to.timezone"

    name = fields.Char(string="Name")


class LeadCustomActivity(models.Model):
    _name = "lead.custom.activity"

    name = fields.Char(string="Activity Name")


class JobProfile(models.Model):
    _name = "job.profile"

    name = fields.Char(string="Profile")


class JobExperience(models.Model):
    _name = "job.experience"

    name = fields.Char(string="Experience")


class NatureExperience(models.Model):
    _name = "nature.experience"

    name = fields.Char(string="Nature of Experience")


class AccountingSoftware(models.Model):
    _name = "accounting.software"

    name = fields.Char(string="Accounting Software")


class TaxSoftware(models.Model):
    _name = "tax.software"

    name = fields.Char(string="Tax Software")


class CommMedium(models.Model):
    _name = "comm.medium"
    
    name = fields.Char(string="Communication Medium")


class SoftwareRemote(models.Model):
    _name = "software.remote"

    name = fields.Char(string="Software Remote Access")


class SoftwareCloud(models.Model):
    _name = "software.cloud"

    name = fields.Char(string="Software Cloud Access")


class SoftwareLocal(models.Model):
    _name = "software.local"

    name = fields.Char(string="Software Local Access")


class DocumentRemote(models.Model):
    _name = "document.remote"

    name = fields.Char(string="Document Remote Access")


class DocumentCloud(models.Model):
    _name = "document.cloud"

    name = fields.Char(string="Document Cloud Access")


class DocumentSharing(models.Model):
    _name = "document.sharing"

    name = fields.Char(string="Document Sharing Access")


class CrmTeam(models.Model):
    _inherit = "crm.team"


class CrmCustomer(models.Model):
    _name = "crm.customer"

    # parent_id = fields.Many2one('crm.lead', string='Parent Task')
    # name = fields.Char(string="Customer Name")
    # contact_name = fields.Char('Contact Name')
    # street = fields.Char('Street')
    # street2 = fields.Char('Street2')
    # zip = fields.Char('Zip', change_default=True)
    # city = fields.Char('City')
    # state_id = fields.Many2one("res.country.state", string='State')
    # country_id = fields.Many2one('res.country', string='Country')
    # phone = fields.Char('Phone')
    # fax = fields.Char('Fax')
    # mobile = fields.Char('Mobile')
    # function = fields.Char('Job Position')
    # title = fields.Many2one('res.partner.title')
    # image = fields.Binary(string="Customer Image")
    # color = fields.Integer('Color Index')
    # opt_out = fields.Boolean(string='Opt-Out', oldname='optout',
    #     help="If opt-out is checked, this contact has refused to receive emails for mass mailing and marketing campaign. "
    #          "Filter 'Available for Mass Mailing' allows users to filter the leads when performing mass mailing.")
    # webform = fields.Char(string="Webform")
    # webinar_id = fields.Many2one('contact.webinar', string="Webinar")


class ContactWebinar(models.Model):
    _name = "contact.webinar"

    name = fields.Char(string="Webinar")


class ServiceProvided(models.Model):
    _name = "service.provided"

    name = fields.Char(string="Service Name")


class CrmAllocation(models.Model):
    _name = "crm.allocation"
    ''' for many2many field allocation '''

    name = fields.Char(string="Name")


class Meeting(models.Model):
    _inherit = 'calendar.event'

    @api.multi
    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time) according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            if meeting.allday:
                meeting.start_date = meeting.start
                meeting.start_datetime = False
                meeting.stop_date = meeting.stop
                meeting.stop_datetime = False

                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop

                meeting.duration = 0.5


class JobInvoicing(models.Model):
    _name = "job.invoicing"

    name = fields.Char(string="Name")


class ClientCredentials(models.Model):
    _name = "client.credentials"

    name = fields.Char(string="Name")
