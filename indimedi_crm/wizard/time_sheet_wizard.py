# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import dateutil.relativedelta
from datetime import date, timedelta, datetime

class ContactMail(models.TransientModel):
    _inherit = 'mail.compose.message'

    mail_partner_id = fields.Many2one('res.partner',string="Contact")
    mail_user_general_manager = fields.Many2one('res.users',string="User")
    mail_lead_owner = fields.Many2one('res.users',string="Lead Owner")
    mail_gm_task = fields.Many2one('res.users',string="Lead Owner")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    project_task = fields.Many2one('project.task',string="Task")

    @api.multi
    def send_mail(self, auto_commit=False):
        template = self.env.ref('indimedi_crm.email_resume_post_sales')
        print ">>>>>>>>>>>>Tempalte IIIIIIIIIIIIIIIIIII",template.id
        if self._context.get('default_model') == 'job.description' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent') and self._context.get('default_template_id') == template.id:
            agreement = self.env['job.description'].browse([self._context['default_res_id']])       
            stage = str(agreement.agreement_stage_id.name)
            if stage == 'Payment Received' or stage == 'New':
                name_stage = self.env['agreement.stage'].search([('name','=','Resume Sent')])
                agreement.with_context(tracking_disable=True).agreement_stage_id = name_stage.id
            self = self.with_context(mail_post_autofollow=True)

        if self._context.get('default_model') == 'time.sheet.wizard' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent'):
            lines_timesheets = inout_obj = self.env['account.analytic.line']
            domain = [('date', '>=', self.start_date),
                    ('date', '<=', self.end_date),('task_id','=',self.project_task.id)]
            inv_lines = inout_obj.search(domain)

            for each in inv_lines:
                if self.end_date:
                    each.with_context(tracking_disable=True).write({'active': False})

            self = self.with_context(mail_post_autofollow=True)

        return super(ContactMail, self).send_mail(auto_commit=auto_commit)


class TimeSheets(models.TransientModel):
    _name = "time.sheet.wizard"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    name = fields.Char('Name')
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    stop_date = fields.Date(string='Stop Date', default=fields.Date.context_today)
    total_all_time = fields.Float(string="Total",store=True)
    project_task = fields.Many2one('project.task',string="Task", required=True)
    email_id = fields.Char(string='Email')
    contact_partner_ids = fields.Many2one('res.partner', string="Partners")
    mail_date = fields.Date('Mail Date', default=datetime.today().strftime(DF))
    mail_sub_date = datetime.today().strftime("%m-%d-%Y")
    daily_sub_date = fields.Date('Mail Date', default=fields.Date.context_today)

    @api.multi
    def print_report(self, data):
        return self.env['report'].get_action(self, 'indimedi_crm.report_timesheet_wizard')

    @api.multi
    def report_data(self):
        inout_obj = self.env['account.analytic.line']
        domain = [('date', '>=', self.start_date),
                 ('date', '<=', self.stop_date),('task_id','=',self.project_task.id)]
        inv_lines = inout_obj.search(domain, order='date,start_time  asc')

        for each in inv_lines:
            if each.unit_amount >= float(0.0):
                total_time = '%s:%02.0f' % tuple(int(round(x)) for x in divmod(each.unit_amount*60,60))
                each.write({'total_time': total_time})
            if each.start_time >= float(0.0):
                start_time_temp = '%s:%02.0f' % tuple(int(round(x)) for x in divmod(each.start_time*60,60))
                each.write({'start_time_temp': start_time_temp})
            if each.stop_time >= float(0.0):
                stop_time_temp = '%s:%02.0f' % tuple(int(round(x)) for x in divmod(each.stop_time*60,60))
                each.write({'stop_time_temp': stop_time_temp})


        sorted_lines = inv_lines.sorted(key=lambda r: r.start_date)
        time_count = sum(sorted_lines.mapped('unit_amount'))
        minutes = round(float(time_count) * 60)
        hours, minutes = divmod(minutes, 60)
        total_all_time = "%02d:%02d"%(hours,minutes)

        self.project_task.total_all_time = total_all_time
        a = sorted_lines.search(domain)
        return sorted_lines
    
    @api.onchange('project_task')
    def _onchange_email_task(self):
        self.email_id = self.project_task.email_id

    @api.multi
    def send_mail_timesheets(self):

        ir_model_data = self.env['ir.model.data']

        template = self.env.ref('indimedi_crm.email_template_worksheets')

        template_id = template.id
        compose_form_ids = ir_model_data.get_object_reference('indimedi_crm', 'email_compose_message_wizard_form_mail_inherit_timesheet')[1]

        # user_name = str(self.project_task.jd_us_name_id.name)
        # server_id = self.project_task.jd_us_name_id.mail_server_id.id
        # mail_auther_id = self.project_task.jd_us_name_id.partner_id.id
        # us_email_id = str(self.project_task.jd_us_name_id.email)

        # user_name = str(self.project_task.jd_us_name_id.name)
        server_id = self.env.user.mail_server_id.id
        mail_auther_id = self.env.user.partner_id.id
        login_email_id = self.env.user.email
        # mail_date = datetime.today().strftime("%m-%d-%Y")


#         print ">>>>>>>>>>>>>>>>>Server ID>>>>>>>>>>>>>", server_id
#         print ">>>>>>>>>>>>>>>>>mail_auther_id>>>>>>>>>>>>>", mail_auther_id
#         print ">>>>>>>>>>>>>>>>>login_email_id>>>>>>>>>>>>>", login_email_id
        # print ">>>>>>>>>>>>>>>>>mail_date>>>>>>>>>>>>>", datetime.today().strftime("%m-%d-%Y"), mail_date


        ctx = dict(email_from = login_email_id, user_name = 'Entigrity Timesheet')
        ctx.update({
                'default_model': 'time.sheet.wizard',
                'default_partner_ids':[(6,0,self.project_task.partner_ids.ids)],
                'default_email_cc': [(6,0,[self.project_task.timesheet_email_id.id] + self.project_task.cc_partner_ids.ids)],
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'default_mail_partner_id': self.project_task.partner_id.id,
                'default_mail_user_general_manager':self.project_task.project_general_manager.id,
                'default_mail_lead_owner':self.project_task.project_general_manager.id,
                'mark_so_as_sent': True,
                'custom_layout': "email_template_worksheets",
                'default_start_date':self.start_date,
                'default_end_date':self.stop_date,
                'default_project_task':self.project_task.id,
                'default_mail_server_id': server_id,
                'default_author_id': mail_auther_id,
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
