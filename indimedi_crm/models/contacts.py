# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

import time
import logging

_logger = logging.getLogger(__name__)

CRM_LIST = []

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_default_country(self):
        company_country_id = self.env['res.country'].search([('code', '=', 'US')], limit=1)
        return company_country_id

    crm_id = fields.Many2one('crm.lead', string="Lead")
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type', readonly=False, store=True)
    pre_sale_contacts = fields.Boolean(string="Pre Sales Contacts", default=True)
    post_sale_contacts = fields.Boolean(string="Post Sales Actual Customer")
    designation_id = fields.Many2one('contact.designation', string="Designation")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    skype_id = fields.Char(string="Skype Id")
    twitter_id = fields.Char(string="Twitter Id")
    linkedin_link = fields.Char(string="LinkedIn")
    facebook_id = fields.Char(string="Facebook")
    personal_email = fields.Char(string="Personal Email")
    street = fields.Char(size=5)
    contact_street3 = fields.Char('Suite/Room No.')
    enrolled_agent = fields.Boolean(string="Enrolled Agent", default=False)
    cpa = fields.Boolean(string="CPA")
    irs_registered = fields.Boolean(string="IRS Registered tax return preparer",default=False)
    tax_attorney = fields.Boolean(string="Tax Attorney", default=False)
    certified_bookkeeper = fields.Boolean(string="Certified BookKeeper", default=False)
    financial_planner = fields.Boolean(string="Financial Planner", default=False)
    others = fields.Boolean(string="Others (Specify)", default=False)
    q_name = fields.Char(string="Name")
    enrolled_agent_license_number = fields.Char("Licence Number")
    cpa_license_number = fields.Char("Licence Number")
    tax_attorney_license_number = fields.Char("Licence Number")
    certified_bookkeeper_license_number = fields.Char("Licence Number")
    financial_planner_license_number = fields.Char("Licence Number")
    others_license_number = fields.Char("Licence Number")
    ptin_number = fields.Char("PTIN Number")
    extension = fields.Char("Extension", size=4)
    company_street = fields.Char('Street')
    company_street2 = fields.Char('Street2')
    company_street3 = fields.Char('Street3')
    company_zip = fields.Char('Zip', change_default=True, size=5)
    company_city = fields.Char('City')
    company_state_id = fields.Many2one("res.country.state", string='State')
    company_country_id = fields.Many2one('res.country', string='Country', default=_get_default_country)
    professional_no = fields.Char(string="Professional No.")
    primary_contact = fields.Boolean(string="Primary Contact")
    #user_id =  fields.Many2one('res.users', string="Lead Owner", default=lambda self: self.env.user)
    comp_owner =  fields.Many2one('res.users', string="Lead Owner",default=lambda self: self.env.user)
    comp_team_id = fields.Many2one('crm.team', string='Lead Owner Team', index=True, track_visibility='onchange')
    comp_source_id = fields.Many2one('utm.source', string='Lead Source')
    # _sql_constraints = [
    #     ('email_uniq', 'unique(email)', 'Official Email must be unique'),
    #     ('personal_email_uniq', 'unique(personal_email)', 'Personal Email must be unique'),
    #     ('phone_uniq', 'unique(phone)', 'Direct Phone Number must be unique'),
    #     ('mobile_uniq', 'unique(mobile)', 'Mobile number must be unique'),
    #     ('professional_no_uniq', 'unique(professional_no)', 'Professional Number must be unique'),
    # ]
    customer_feedback = fields.One2many('customer.feedback','customers',string='Feedback',track_visibility='onchnage')
    timesheet_mail = fields.Boolean(string="Timesheet Contact")

    #new fields
    category = fields.Selection([
                        ('accounting','ACCOUNTING FIRM'),
                        ('business','Business'),
                        ('government','Government/Colleges/Others'),
                        ('cpa', 'CPA Firm'),
                        ('Accounting Firm (EA - Tax - Bookkeeping Firm)', 'Accounting Firm (EA - Tax - Bookkeeping Firm)'),
                        ('Affiliate - Vendor - Partner', 'Affiliate - Vendor - Partner'),
                        ('Law Firm', 'Law Firm'),
                        ('Financial Planning Firm', 'Financial Planning Firm'),
                        ('Staffing Firm', 'Staffing Firm')
                        ], string="Category")
    data_lable_ids = fields.Many2many('crm.lead.tag', string='Data Label', help="Classify and analyze your lead/opportunity categories like: Training, Service")
    contact_type = fields.Selection([('primary', 'Decision Maker'),
                                     ('influencer', 'Influencer'),
                                     ('reporting', 'Reporting Manager')], string="Type")
    
    
    
    @api.onchange('contact_type')
    def onchange_contact_type(self):
        if self.contact_type:
            if self.contact_type == 'primary':
                self.primary_contact = True
            else:
                self.primary_contact = False
    
    @api.model
    def create(self, vals):
        _logger.debug("Creating new contact user")
        if vals.get('phone'):
            track_list  = []
            for i in vals.get('phone'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Direct Phone.'))
                if len(track_list) > 10:
                    raise ValidationError(_('Not Valid Direct Phone.'))
            phone_str = vals['phone']
            phone_str = phone_str.replace('-', '').replace('-', '')
            phone = phone_str[0:3] + '-' + phone_str[3:6] + '-' + phone_str[6:10]
            vals['phone'] = phone
        if vals.get('mobile'):
            track_list  = []
            for i in vals.get('mobile'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Mobile.'))
                if len(track_list) > 10:
                    raise ValidationError(_('Not Valid Mobile.'))
            mobile_str = vals['mobile']
            mobile_str = mobile_str.replace('-', '').replace('-', '')
            mobile = mobile_str[0:3] + '-' + mobile_str[3:6] + '-' + mobile_str[6:10]
            vals['mobile'] = mobile
        partner = super(Partner, self).create(vals)

        # if vals['mobile']:
        #     vals['mobile'] = vals['mobile'][0:3] + '-' + vals['mobile'][3:6] + '-' + vals['mobile'][6:10]
        lead_obj = self.env['crm.lead']
        #Lead create automatically when customer is company
        if partner.company_type == 'company':
            _logger.debug("selected comapny in the new contact user")
            
            lead = lead_obj.create({
                       'name': partner.name,
                       'lead_partner_id': partner.id,
                       # set lead address as company address
                       'c_street': partner.company_street,
                       'c_street2': partner.company_street2,
                       'c_street3': partner.company_street3,
                       'c_city': partner.company_city,
                       'c_state_id': partner.company_state_id.id,
                       'c_zip': partner.company_zip,
                       'c_country_id': partner.company_country_id.id,
                       'parent_id': partner.id,
                       'email_from':partner.email,
                       'phone':partner.phone,
                       'allocation_rs':True, #default RS in allocation
                       'lead_website': partner.website,
                       'lead_fax': partner.fax,
                       'lead_twitter': partner.twitter_id,
                       'user_id':partner.comp_owner.id,
                       'team_id':partner.comp_team_id.id,
                       'source_id':partner.comp_source_id.id,
                       'category': partner.category,
                       'tag_ids': partner.data_lable_ids.ids,
                       
                    })
            # lead_obj = self.env['crm.lead'].search([('parent_id', '!=', False), ('parent_id', '=', partner.parent_id.id)])
            # print ">>>>>> lead_obj >>>", lead_obj, partner.id
            # if lead_obj:
            #   print "if lead_obj>>>>>>>>>>>>"
            #   lead_obj.write({'child_ids': [(0,0,{
            #          'name': partner.name,
            #          'title': partner.title.id,
            #          'designation_id': partner.designation_id.id,
            #          'email': partner.email,
            #          'phone': partner.phone,
            #          'mobile': partner.mobile,
            #          'parent_id': True,})]
            #       })
            _logger.debug("lead created for the new contact user")
        else:
            if partner.parent_id:
                if not partner.parent_id.company_street:
                    partner.parent_id.company_street = partner.company_street
                    partner.parent_id.company_street2 = partner.company_street2
                    partner.parent_id.company_street3 = partner.company_street3
                    partner.parent_id.company_zip = partner.company_zip
                    partner.parent_id.company_city = partner.company_city
                    partner.parent_id.company_state_id = partner.company_state_id
                    partner.parent_id.company_country_id = partner.company_country_id
                    partner.parent_id.website = partner.website
                    partner.parent_id.email = partner.email
                    partner.parent_id.phone = partner.phone

        return partner

    @api.one
    def write(self, vals):
        # if self.is_company:
        #     for partner in self:
        if vals.get('phone'):
            track_list  = []
            for i in vals.get('phone'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Direct Phone.'))
                if len(track_list) > 12:
                    raise ValidationError(_('Not Valid Direct Phone.'))
            phone_str = vals['phone']
            phone_str = phone_str.replace('-', '').replace('-', '')
            phone = phone_str[0:3] + '-' + phone_str[3:6] + '-' + phone_str[6:10]
            vals['phone'] = phone
        if vals.get('mobile'):
            track_list  = []
            for i in vals.get('mobile'):
                track_list.append(i)
            for j in track_list :
                if(j not in ['0','1','2','3','4','5','6','7','8','9','-']):
                    raise ValidationError(_('Not Valid Mobile.'))
                if len(track_list) > 12:
                    raise ValidationError(_('Not Valid Mobile.'))
            mobile_str = vals['mobile']
            mobile_str = mobile_str.replace('-', '').replace('-', '')
            mobile = mobile_str[0:3] + '-' + mobile_str[3:6] + '-' + mobile_str[6:10]
            vals['mobile'] = mobile
        partner = super(Partner, self).write(vals)
        if self.parent_id:
            if not self.parent_id.company_street:
                self.parent_id.company_street = self.company_street
                self.parent_id.company_street2 = self.company_street2
                self.parent_id.company_street3 = self.company_street3
                self.parent_id.company_zip = self.company_zip
                self.parent_id.company_city = self.company_city
                self.parent_id.company_state_id = self.company_state_id
                self.parent_id.company_country_id = self.company_country_id
                self.parent_id.website = self.website
                self.parent_id.email = self.email
                self.parent_id.phone = self.phone

        partner_name = str(self.name)
        lead_add_obj = self.env['crm.lead'].search([('name', '=', partner_name)])
        comp_add = lead_add_obj.write({
                   # set company address as lead address
                    'c_street': self.company_street,
                    'c_street2': self.company_street2,
                    'c_street3': self.company_street3,
                    'c_city': self.company_city,
                    'c_state_id': self.company_state_id.id,
                    'c_zip': self.company_zip,
                    'c_country_id': self.company_country_id.id,
                    'email_from': self.email,
                    'phone': self.phone,
                    'lead_website': self.website,
                    'lead_fax': self.fax,
                    'lead_twitter': self.twitter_id,
                    'user_id':self.comp_owner.id,
                    'team_id':self.comp_team_id.id,
                    'source_id':self.comp_source_id.id,
                })
        return partner

    # @api.onchange('mobile')
    # def _onchange_mobile(self):
    #     if self.mobile:
    #         self.mobile = self.mobile[0:3] + '-' + self.mobile[3:6] + '-' + self.mobile[6:10]

    # @api.onchange('phone')
    # def _onchange_phone(self):
    #     if self.phone:
    #         self.phone = self.phone[0:3] + '-' + self.phone[3:6] + '-' + self.phone[6:10]


    @api.onchange('parent_id')
    def _onchange_address_contact(self):
        if self.parent_id:
            self.company_street = self.parent_id.company_street
            self.company_street2 = self.parent_id.company_street2
            self.company_street3 = self.parent_id.company_street3
            self.company_zip = self.parent_id.company_zip
            self.company_city = self.parent_id.company_city
            self.company_state_id = self.parent_id.company_state_id
            self.company_country_id = self.parent_id.company_country_id

    #Post Sales button action
    @api.multi
    def post_sale(self):
        self.pre_sale_contacts = False
        self.post_sale_contacts = True
        return


class ContactDesignation(models.Model):
    _name = 'contact.designation'

    name = fields.Char(string="Designation")
