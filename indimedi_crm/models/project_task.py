# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = 'project.project'

    client_name = fields.Char(string='Client Name')
    sales_manager_id = fields.Many2one('res.users', string="Sales Manager", track_visibility='onchange')
    jd_us_name_id = fields.Many2one('res.users', string="US Name", track_visibility='onchange')
    jd_ea_working_id = fields.Many2one('res.users', string="EA Working", track_visibility='onchange')
    project_general_manager = fields.Many2one('res.users', string="General Manager", track_visibility='onchange')
    timesheet_email_id = fields.Many2one('res.partner', string="Timesheet Email", track_visibility='onchange')
    timesheet_phone = fields.Char('Employee Phone', track_visibility='onchange')
    invoicing_type_id = fields.Many2one('job.invoicing', string="Invoicing Type", track_visibility='onchange')
    invoice_start_date = fields.Date(string="Billing Start Date", track_visibility='onchange')
    hour_selection = fields.Selection([('5','5 Hours'),('10','10 Hours'),('15', '15 Hours'),('20','20 Hours'),('25', '25 Hours'),('30','30 Hours'),
                                       ('40','40 Hours'),('80','80 Hours'),('90','90 Hours'),
                                       ('100','100 Hours'),('40_20','40-20 Hours'),
                                       ('20_10','20-10 Hours'),('160','160 Hours'),
                                       ('180','180 Hours'),('200','200 Hours')],
                                       string="Working Hours", track_visibility='onchange')
    rate_per_hour = fields.Float(string="Rate Per Hour", track_visibility='onchange')
    total_rate = fields.Float('Total Min. Rate', track_visibility='onchange')
    client_email = fields.Char(string="Client Email", track_visibility='onchange')

    #new fields
    billing_history_ids = fields.One2many('billing.history', 'project_id', string="Billing History")
    invoice_end_date = fields.Date(string="Billing End Date", track_visibility='onchange')
    date_of_join = fields.Date(string="Date of Joining")
    date_of_join_dummy = fields.Date(string="Date of Joining Dummy")
    client_priority = fields.Selection([('high', 'High'),
                                        ('medium', 'Medium'),
                                        ('low', 'Low')], string="Priority")
    client_firm = fields.Selection([('big', 'Big Firm'),
                                    ('normal', 'Normal Firm'),
                                    ('small', 'Small Firm')], string="Client Firm")
    subsidiary_id = fields.Many2one('subsidiary.master', string="Billing Company")
    is_expired = fields.Boolean(compute='_check_project_expiry', string="Expired", search='_value_search_expired')
    on_notice = fields.Boolean(compute='_check_on_notice', string="On Notice", search='_value_search_notice')
    dummy_start_date = fields.Date(string="Dummy Start Date")
    last_invoice_id = fields.Many2one('timesheet.invoice', string="Last Invoice")
    permenant_or_not = fields.Selection([('temporary', 'Temporary'),
                                         ('permanent', 'Permanent')], compute='_check_on_notice', string="Temporary/Permanent")
    
    
    @api.multi
    def _value_search_expired(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.is_expired is True )
        if recs:
            return [('id', 'in', [x.id for x in recs])]
           
    @api.multi
    def _value_search_notice(self, operator, value):
        recs = self.search([]).filtered(lambda x : x.on_notice is True )
        if recs:
            return [('id', 'in', [x.id for x in recs])]
           
           
    @api.multi
    def _check_on_notice(self):
        for rec in self:
            if rec.invoice_end_date:
                rec.on_notice = True
                rec.permenant_or_not = 'temporary'
            else:
                rec.permenant_or_not = 'permanent'
    
    @api.multi
    def _check_project_expiry(self):
        for rec in self:
            today = fields.Date.to_string(datetime.now().date())
            if rec.invoice_end_date:
                if rec.invoice_end_date < today:
                    rec.is_expired = True
    
    @api.multi
    def open_billing_wizard(self):
        view_id = self.env.ref('indimedi_crm.change_billing_info_form')
        
        return {
                'name': "Change Billing Information",
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'change.billing.info',
                'view_id': view_id.id,
                'target': 'new',
                'context': {'default_project_id': self.id},
        }
        
    @api.multi
    def write(self, vals):
        #Employee Phone Number Format Logic
        if vals.get('timesheet_phone'):
            track_list  = []
            for i in vals.get('timesheet_phone'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Employee Phone Number.'))
                if len(track_list) > 12:
                    raise ValidationError(_('Not Valid Employee Phone Number.'))
            phone_str = vals['timesheet_phone']
            phone_str = phone_str.replace('-', '').replace('-', '')
            phone = phone_str[0:3] + '-' + phone_str[3:6] + '-' + phone_str[6:10]
            vals['timesheet_phone'] = phone
        if vals.get('date_of_join_dummy'):
            if not self.date_of_join:
                vals['date_of_join'] = vals.get('date_of_join_dummy') 
        res = super(Project, self).write(vals)
        return res

class ProjectTask(models.Model):
    _inherit = 'project.task'

    jd_us_name_id = fields.Many2one(related='project_id.jd_us_name_id', string="US Name", track_visibility='onchange' ,store=True)
    jd_manager_id = fields.Many2one(related='project_id.user_id', string="Manager", track_visibility='onchange',store=True)
    jd_profile = fields.Char(string="Designation")
    # date = fields.Date(string="Date",required=True,default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    # for task date in task form
    task_date = fields.Date(string="Date",required=True,default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    client_reporting_id = fields.Many2one('res.partner', string="Client Reporting", track_visibility='onchange')
    task_id = fields.Many2one('project.task', track_visibility='onchange')
    email_id = fields.Char(string="Email Id", placeholder="mymail@mail.com")
    phone = fields.Char('Phone')
    profile_id = fields.Char('Designation')
    total_all_time = fields.Char(string="Total")
    partner_ids = fields.Many2many('res.partner', string='Mail To')
    credential_ts = fields.One2many('credentials.timesheet', 'credential_task_id', string="Credentials")
    project_general_manager = fields.Many2one(related='project_id.project_general_manager', string="General Manager", track_visibility='onchange' ,store=True)
    task_sales_manager_id = fields.Many2one(related='project_id.sales_manager_id', string="Sales Manager", track_visibility='onchange' ,store=True)
    mail_work = fields.Char(string='Mail Work')
    timesheet_email_id = fields.Many2one(related='project_id.timesheet_email_id', string="Timesheet Email", track_visibility='onchange',store=True)
    timesheet_phone = fields.Char(related='project_id.timesheet_phone', string="Employee Phone", track_visibility='onchange',store=True)
    user_id = fields.Many2one(related='project_id.jd_ea_working_id', string='Assigned to',
        default=lambda self: self.env.uid, index=True, track_visibility='always', store=True)
    partner_id = fields.Many2one(related='project_id.partner_id', string='Customer', track_visibility='onchange',store=True)
    cc_partner_ids = fields.Many2many('res.partner','timesheet_cc_partner_rel', 'partner_id','cc_partner_id', string="Mail CC", store=True)

    comm_on_email = fields.Boolean(string="Email")
    comm_on_phone = fields.Boolean(string="Phone")
    comm_on_chat = fields.Boolean(string="Chat")
        
    @api.model
    def create(self, vals):
        client = super(ProjectTask, self).create(vals)
        if client.partner_id:
            partner_id = self.env['res.partner'].search([('parent_id','=',client.partner_id.id),('primary_contact','=',True)], limit=1)
            if partner_id:
                #for default value set in client_reporting_id
                client.client_reporting_id = partner_id.id
                #for default value set in partner_ids(Mail To)
                client.write({'partner_ids': [(4, partner_id.id)]})

        return client

    @api.multi
    def unlink(self):
        if self.project_id:
            for rec in self:
                rec.project_id.active = False
        return super(ProjectTask, self).unlink()

    # @api.onchange('task_date')
    # def _onchnahge_dates(self):
    #     task_date = datetime.strptime(self.task_date, '%Y-%m-%d').date()
    #     timesheets = self.env['account.analytic.line'].search([('task_id','=',self._origin.id)])
    #     date_wise_timesheet = []
    #     for each_timesheet in timesheets:
    #         each_date = datetime.strptime(each_timesheet.date, '%Y-%m-%d').date()
    #         if each_date == task_date:
    #             print "\n===========ACCOUNT ID===========",each_timesheet.account_id
    #             date_wise_timesheet.append(each_timesheet)
    #     for each in date_wise_timesheet:
    #         print "\n+++++++++++++",each.account_id
    #     print "\n===========>",date_wise_timesheet
        
    #     final_data = [{'date': each.date, 'user_id': each.user_id.id, 'type_of_view': each.type_of_view, 'start_time': each.start_time, 'stop_time': each.stop_time, 'name': str(each.name), 'unit_amount': each.unit_amount,'account_id': each.account_id.id,'amount':each.amount} for each in date_wise_timesheet]
    #     print "\n===========>Final",final_data
    #     self.update({
    #         'timesheet_ids' : [(0, 0, val) for val in final_data],
    #         })
    #     # 'default_order_line': [(0, 0, val) for val in order_lines],



    @api.model
    def open_form_from_kanban(self):
        action = self.env.ref('project.action_view_task').read()[0]
        tasks = self.env['project.task'].search([('user_id', '=', self._uid)])
        if len(tasks) == 1:
            action['views'] = [(self.env.ref('project.view_task_form2').id, 'form')]
            action['res_id'] = tasks[0].id
        return action

class ClientReporting(models.Model):
    _name = 'client.reporting'

    name = fields.Char(string="Name")

class CredentialsTask(models.Model):
    _name = 'credentials.task'

    name = fields.Char(string='Name')

class CredentialsTimsheet(models.Model):
    _name = 'credentials.timesheet'

    # name = fields.Char(string='Name')
    cred_timesheet = fields.Many2one('credentials.task', string="Name")
    cred_description = fields.Text(name="Description")
    credential_task_id = fields.Many2one('project.task', string='Tasks')
    attachment = fields.Binary(string='File')
