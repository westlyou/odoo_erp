# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import os.path
from odoo.addons.website_form.controllers.main import WebsiteForm
# from Tkinter import *
# import tkMessageBox
import logging
import requests
import json
import httpagentparser
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.web.controllers.main import serialize_exception, content_disposition
import base64
import odoo.addons.web.controllers.main as main
import odoo

_logger = logging.getLogger(__name__)
    
    
# class Home(main.Home):
    
#     
#     @http.route('/client', type='http', auth="public")
#     def web_signup(self, redirect=None, **kw):
#         request.params['login_success'] = False
#         if request.httprequest.method == 'GET' and redirect and request.session.uid:
#             return http.redirect_with_hash(redirect)
# 
#         if not request.uid:
#             request.uid = odoo.SUPERUSER_ID
# 
#         values = request.params.copy()
#         try:
#             values['databases'] = http.db_list()
#         except odoo.exceptions.AccessDenied:
#             values['databases'] = None
# 
#         if request.httprequest.method == 'POST':
#             old_uid = request.uid
#             
#             login = request.params['login']
#             
#             user_id = request.env['res.users'].sudo().search([('login', '=', login), ('is_client', '=', True)])
#             print"user_id============",user_id.password
#             if user_id:
#                 request.params['password'] = 'aa'
#                 uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
#             else:
#                 if not request.params.get('password'):
#                     values['error'] = _("Email Not Found!")
#                     return request.render('web.client_signup', values)
#                 uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
#             if uid is not False:
#                 request.params['login_success'] = True
#                 if not redirect:
#                     redirect = '/web'
#                 return http.redirect_with_hash(redirect)
#             request.uid = old_uid
#             values['error'] = _("Wrong login/password")
#         return request.render('web.client_signup', values)
#     

class AgreementConfirm(http.Controller):
    
    @http.route('/download-signup-t-c', type='http', auth="public")
    @serialize_exception
    def download_t_c(self, **kw):
        sighup_pdf = request.env['ir.attachment'].search([('res_model', '=', 'res.company'),
                                                        ('res_field', '=', 'signup_tc'),
                                                        ('res_id', '=', 1)])
        
        if not sighup_pdf:
            return request.not_found()
        filename = 'ENTIGRITY REMOTE STAFFING SIGN UP TERMS.pdf'
        Model = request.registry['ir.attachment']
        fields = ['datas']
        res = Model.read(sighup_pdf, fields)[0]
        
        filecontent = base64.b64decode(res.get('datas') or '')
        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % ('ir.attachment'.replace('.', '_'), id)
        return request.make_response(filecontent,
                       [('Content-Type', 'application/octet-stream'),
                        ('Content-Disposition', content_disposition(filename))])

    @http.route('/agreement_done/<agreement>/<token>', type='http', auth='public', website=True)
    def agreement_yes(self, agreement, token, **post):
        data = {}
        ip = request.httprequest.environ["REMOTE_ADDR"]
#         ip = request.httprequest.remote_addr
        
        # get browser info
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        
        # get device info
        platform = browser['os']['name']
        browser_name = browser['browser']['name']
        
        device_name = browser_name + " via " + platform
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement), ('random_token', '=', token)])
        if not agreement_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Access Token!"})
        if agreement_id.agree:
            return request.render('indimedi_crm.already_agreed', data)
        
        # get IP Info
#         send_url = 'http://api.ipstack.com/check?access_key=53ef5675bc86a5f8ae76707f13060ae0&format=1'
#         r = requests.get(send_url)
#         j = json.loads(r.text)
#         
#         ip_info = ''
#         if j.get('ip'):
#             ip = j.get('ip')
#             ip_info = j 
#         else:
        ip = request.httprequest.environ["REMOTE_ADDR"] 
        today = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        
        vals = {'agree': True,
               'ip_add_of_user': ip,
#                'ip_info': ip_info,
               'device_name': device_name,
               'signed_at': today + " UTC"}
        
        agreement_id.sudo().write(vals)
        
        # send signup confirmation email
        template_id = request.env.ref('indimedi_crm.email_template_agreement_crm_signup_confirm').sudo()
        email_vals = template_id.sudo().generate_email(agreement_id.id)
        
        
        email_vals['attachment_ids'] = [(6, 0, [20554])]  # 20554 server | local 19561
        email_vals['email_from'] = agreement_id.crm_id.user_id.email
        email_vals['user_name'] = agreement_id.crm_id.user_id.name
        email_vals['email_to'] = agreement_id.get_contact_email()
        email_vals['email_partner_cc'] = [(6,0, agreement_id.crm_id.user_id.company_id.signup_email_cc.ids)]
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        # send device info email
        template_id = request.env.ref('indimedi_crm.email_template_agreement_crm_signup_device').sudo()
        email_vals = template_id.sudo().generate_email(agreement_id.id)
         
        
        email_vals['email_from'] = agreement_id.crm_id.user_id.email
        email_vals['email_to'] = agreement_id.get_contact_email()
        email_vals['email_partner_cc'] = [(6,0, agreement_id.crm_id.user_id.company_id.signup_email_cc.ids)]
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        if agreement:
            data = {'agreement': agreement}
            
        #send notification to lead owner about confirmation
        template_id = request.env.ref('indimedi_crm.signup_confimed_notification')
        
        ctx = dict(email_from=agreement_id.crm_id.user_id.email,
                        user_name=agreement_id.crm_id.user_id.name,
                        )  # 20554 server
             
        ctx.update({
                'default_model': 'job.description',
                'default_res_id': agreement_id.ids[0],
#                     'default_use_template': bool(template_id),
#                     'default_template_id': template_id,
#                     'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "email_template_agreement_crm",
                'email_to' : agreement_id.crm_id.user_id.email,  # default set recepient as company email in template
        })
        
        email_vals = template_id.with_context(ctx).sudo().generate_email(agreement_id.id)
#         email_vals['attachment_ids'] = [(6,0, [20554])]
        email_vals['email_partner_cc'] = [(6,0, agreement_id.crm_id.user_id.company_id.signup_email_cc.ids)]
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        return request.render('indimedi_crm.i_agree', data)
    
    @http.route('/staff_confirmation/<agreement>/<token>', type='http', auth='public', website=True)
    def staff_confirmation(self, agreement, token, **post):
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement), ('token_staff_confirm', '=', token), ('active', '=', False)])
        
        if agreement_id.is_client_confim:
            return request.render('indimedi_crm.confirmation_detail_submited', {})
        
        if not agreement_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Access Token!"})
        
        data = {'agreement': agreement, 'token': token}
        return request.render('indimedi_crm.staff_confirmation_form', data)
    
    @http.route('/staff_confirmed/<agreement>/<token>', type='http', auth='public', website=True, csrf=False)
    def staff_confirmed(self, agreement, token, **post):
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement), ('token_staff_confirm', '=', token), ('active', '=', False)])
        if not agreement_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Access Token!"})
        
        vals = {
                'agreement': agreement,
                'token': token,
                }
        
        if agreement_id.is_client_confim:
            return request.render('indimedi_crm.confirmation_detail_submited', vals)
        
        if not post.get('payment_type'):
            vals.update({'error': "Please select payment type!"})
            return request.render('indimedi_crm.staff_confirmation_form', vals)
        
        # get IP Information of device
        ip = request.httprequest.environ["REMOTE_ADDR"]
#         ip = request.httprequest.remote_addr
        
        # get browser info
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        
        # get device info
        platform = browser['os']['name']
        browser_name = browser['browser']['name']
        
        device_name = browser_name + " via " + platform
        
        # get IP Info
        send_url = 'http://api.ipstack.com/check?access_key=53ef5675bc86a5f8ae76707f13060ae0&format=1'
        r = requests.get(send_url)
        j = json.loads(r.text)
        
        ip_info = ''
        if j.get('ip'):
            ip = j.get('ip')
            ip_info = j 
        else:
            ip = request.httprequest.environ["REMOTE_ADDR"] 
        today = datetime.strftime(datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        
        if post.get('payment_type') == 'bank':
            payment_type = post.get('payment_type')
            name_of_account = post.get('name_of_account')
            account_number = post.get('account_number')
            name_of_bank = post.get('name_of_bank')
            type_of_bank = post.get('type_of_bank')
            bank_routing = post.get('bank_routing')
            
            payment_vals = {
                            'payment_method': payment_type,
                            'name_of_account':name_of_account,
                            'account_number': account_number,
                            'name_of_bank': name_of_bank,
                            'type_of_bank':type_of_bank,
                            'bank_routing':bank_routing,
                            'ip_add_of_user': ip,
                           'device_name': device_name,
                           'signed_at': today + " UTC",
                            'is_client_confim': True
                            }
            agreement_id.with_context({'bypass_write': True}).write(payment_vals)
        
        if post.get('payment_type') == 'credit_card':
            payment_type = post.get('payment_type')
            name_on_card = post.get('name_on_card')
            card_number = post.get('card_number')
            type_of_card = post.get('type_of_card')
            expiry_month = post.get('expiry_month')
            expiry_year = post.get('expiry_year')
            cvv = post.get('cvv')
            pin = post.get('pin')
            
            payment_vals = {
                            'payment_method': payment_type,
                            'name_on_card': name_on_card,
                            'card_number':card_number,
                            'type_of_card': type_of_card,
                            'expiry_month': expiry_month,
                            'expiry_year': expiry_year,
                            'cvv':cvv,
                            'pin':pin,
                            'ip_add_of_user': ip,
                            'device_name': device_name,
                            'signed_at': today + " UTC",
                            'is_client_confim': True
                            }
            agreement_id.with_context({'bypass_write': True}).write(payment_vals)
        
        # send mail to client with device info
        template_id = request.env.ref('indimedi_crm.signing_confirmation_of_staff')
        
        ctx = dict(email_from=agreement_id.agreement_general_manager.email,
                        user_name=agreement_id.agreement_general_manager.name,
                        )  # 20554 server
             
        ctx.update({
                'default_model': 'job.description',
                'default_res_id': agreement_id.ids[0],
#                     'default_use_template': bool(template_id),
#                     'default_template_id': template_id,
#                     'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "email_template_agreement_crm",
                'email_to' : agreement_id.jd_email,  # default set recepient as company email in template
                'email_partner_cc': [(6,0, agreement_id.crm_id.user_id.company_id.staff_confirmation_email_cc.ids)]
        })
        
        email_vals = template_id.with_context(ctx).sudo().generate_email(agreement_id.id)
#         email_vals['attachment_ids'] = [(6,0, [20554])]
#         email_vals['email_partner_cc'] = [(6,0, agreement_id.user_id.company_id.staff_confirmation_email_cc.ids)]
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        #send notification to manager about confirmation
        template_id = request.env.ref('indimedi_crm.staff_confimed_notification')
        
        ctx = dict(email_from=agreement_id.agreement_general_manager.email,
                        user_name=agreement_id.agreement_general_manager.name,
                        )  # 20554 server
             
        ctx.update({
                'default_model': 'job.description',
                'default_res_id': agreement_id.ids[0],
#                     'default_use_template': bool(template_id),
#                     'default_template_id': template_id,
#                     'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "email_template_agreement_crm",
                'email_to' : agreement_id.agreement_general_manager.email,  # default set recepient as company email in template
        })
        
        email_vals = template_id.with_context(ctx).sudo().generate_email(agreement_id.id)
#         email_vals['attachment_ids'] = [(6,0, [20554])]
        email_vals['email_partner_cc'] = [(6,0, agreement_id.crm_id.user_id.company_id.staff_confirmation_email_cc.ids)]
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
         
        return request.render('indimedi_crm.staff_confirmed', vals)
    
    
class MailMail(http.Controller):

    @http.route([ '/indimedi_crm/data'], methods=['GET'], type='http', auth="none", website=True,)
    def index(self, **get):
        ''' Calls when click agree button from mail template. '''
        print "\n=======>SElf", self
        agreement_id = get['agreement_id']
        ref_no = request.env['job.description'].sudo().browse(int(agreement_id)).name
        email_id = request.env['job.description'].sudo().browse(int(agreement_id)).crm_id.email_from
        _logger.info("1111**************************************")
        print "Ref....................", ref_no
        # for fetch ip of user who do click on i agree
        if "HTTP_X_FORWARDED_FOR" in request.httprequest.environ:
            # Virtual host   
            ip = request.httprequest.environ["HTTP_X_FORWARDED_FOR"]
            _logger.debug(">>>>HTTP_X_FORWARDED_FOR>>>>>>>")
            _logger.info("2222**************************************")
            print "IPPPPPPPPPPPPPPPPPPPPP", ip
        elif "HTTP_HOST" in request.httprequest.environ:
            # Non-virtualhost
            ip = request.httprequest.environ["REMOTE_ADDR"]
            _logger.debug(">>>>HTTP_HOST>>>>>>>")
            _logger.info("3333**************************************")
            print "IPPPPPPPPPPPPPPPPPPPPP", ip
        return request.render("indimedi_crm.page_action", {
            'refnumber': ref_no ,
            'mail' : email_id,
            'ip':ip,
        })

    @http.route([ '/action_page'], methods=['GET'], type='http', auth="public", website=True,)
    def index_page(self, **get):   
        ref_number = get['refnumber']
        mail = get['mail']
        ip = get['ip']
        agree_name = get['name']
        job_id = request.env['job.description'].sudo().search([('name', '=', ref_number)])
        c_name = job_id.jd_company
        comp_name = request.env['res.partner'].sudo().search([('name', '=', c_name)])
        comp_name.write({'pre_sale_contacts':False, 'post_sale_contacts':True})  # move to in customers and set post sales true after agree
        print 'Company Name', comp_name
        job_id.write({'agree': True,
            'jd_mail_from':mail,
            'ip_add_of_user':ip,
            'agree_name':agree_name})
        if job_id.agree:
            job_id.send_mail_templates()  # send mails to smtp user and other on agree
            # job_id.active = False # transfer lead to post sales after agree
            # job_id.crm_id.to_be_post_sales = True # transfer lead to post sales after agree

        # if not job_id.agree:
        #     window = Tk()
        #     window.wm_withdraw()
        #     window.geometry("1x1+200+200")#remember its .geometry("WidthxHeight(+or-)X(+or-)Y")
        #     tkMessageBox.showerror(title="Warning",message="Ref number is not proper",parent=window)
        #     return request.render("indimedi_crm.page_action", {
        #        })
        return http.local_redirect("http://www.entigrity.com/payment/")  # redirect payment link on  I agree click

    # @http.route(['/go_to_payment'], type='http', auth="public", website=True,)
    # def make_payment(self, **kw):
    #     print "\n==>BHOOMMM"
    #     return http.local_redirect("https://www.google.com/")
    
