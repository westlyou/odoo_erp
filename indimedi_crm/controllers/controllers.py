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


_logger = logging.getLogger(__name__)
    

class AgreementConfirm(http.Controller):
#     @http.route('/agreement_confirm/<agreement>/<token>', type='http', auth='public', website=True)
#     def agreement_confirm(self, agreement, token, **post):
#         data = {}
#         job_id = request.env['job.description'].search([('id', '=', agreement),('random_token', '=', token)])
#         
#         if job_id.agree:
#             return request.render('indimedi_crm.already_agreed', data)
#         
#         if not job_id:
#             return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Agreement Access Token!"})
#         data = {'agreement': agreement, 'token': token}
#         return request.render('indimedi_crm.i_agree_form', data)
    
    
    @http.route('/agreement_done/<agreement>/<token>', type='http', auth='public', website=True)
    def agreement_yes(self, agreement, token, **post):
        data = {}
        ip = request.httprequest.environ["REMOTE_ADDR"]
#         ip = request.httprequest.remote_addr
        
        #get browser info
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        
        #get device info
        platform = browser['os']['name']
        browser_name = browser['browser']['name']
        
        device_name = browser_name + " via " + platform
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement),('random_token', '=', token)])
        if not agreement_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Access Token!"})
        if agreement_id.agree:
            return request.render('indimedi_crm.already_agreed', data)
        
        #get IP Info
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
        
        vals = {'agree': True,
               'ip_add_of_user': ip,
#                'ip_info': ip_info,
               'device_name': device_name,
               'signed_at': today + " UTC"}
        
        agreement_id.sudo().write(vals)
        
        #send signup confirmation email
        template_id = request.env.ref('indimedi_crm.email_template_agreement_crm_signup_confirm').sudo()
        email_vals = template_id.sudo().generate_email(agreement_id.id)
        
        superuser_id = request.env['res.users'].sudo().search([('id', '=', 1)])
        
        email_vals['attachment_ids'] = [(6,0, [20554])] #20554 server | local 19561
        email_vals['email_from'] = superuser_id.email
        email_vals['email_to'] = agreement_id.crm_id.email_from
        
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        #send device info email
        template_id = request.env.ref('indimedi_crm.email_template_agreement_crm_signup_device').sudo()
        email_vals = template_id.sudo().generate_email(agreement_id.id)
         
        superuser_id = request.env['res.users'].sudo().search([('id', '=', 1)])
        
        email_vals['email_from'] = superuser_id.email
        email_vals['email_to'] = agreement_id.crm_id.email_from
        
        mail_id = request.env['mail.mail'].sudo().create(email_vals)
        mail_id.send()
        
        if agreement:
            data = {'agreement': agreement}
        return request.render('indimedi_crm.i_agree', data)
    
    
    @http.route('/staff_confirmation/<agreement>/<token>', type='http', auth='public', website=True)
    def staff_confirmation(self, agreement, token, **post):
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement),('token_staff_confirm', '=', token),('active', '=', False)])
        
        if agreement_id.is_client_confim:
            return request.render('indimedi_crm.confirmation_detail_submited', {})
        
        if not agreement_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Access Token!"})
        
        data = {'agreement': agreement, 'token': token}
        return request.render('indimedi_crm.staff_confirmation_form', data)
    
    @http.route('/staff_confirmed/<agreement>/<token>', type='http', auth='public', website=True, csrf=False)
    def staff_confirmed(self, agreement, token, **post):
        agreement_id = request.env['job.description'].sudo().search([('id', '=', agreement),('token_staff_confirm', '=', token),('active', '=', False)])
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
                            'is_client_confim': True
                            }
            agreement_id.with_context({'bypass_write': True}).write(payment_vals)
            
        if post.get('payment_type') == 'credit_card':
            name_on_card = post.get('name_on_card')
            card_number = post.get('card_number')
            type_of_card = post.get('type_of_card')
            expiry_date = post.get('expiry_date')
            cvv = post.get('cvv')
            pin = post.get('pin')
            
            payment_vals = {
                            'payment_method': payment_type,
                            'name_on_card': name_on_card,
                            'card_number':card_number,
                            'type_of_card': type_of_card,
                            'expiry_date': expiry_date,
                            'cvv':cvv,
                            'pin':pin,
                            'is_client_confim': True
                            }
            agreement_id.with_context({'bypass_write': True}).write(payment_vals)
            
        return request.render('indimedi_crm.staff_confirmed', vals)
    
    
class MailMail(http.Controller):
    @http.route([ '/indimedi_crm/data'], methods=['GET'], type='http', auth="none", website=True,)
    def index(self, **get):
        ''' Calls when click agree button from mail template. '''
        print "\n=======>SElf",self
        agreement_id = get['agreement_id']
        ref_no = request.env['job.description'].sudo().browse(int(agreement_id)).name
        email_id = request.env['job.description'].sudo().browse(int(agreement_id)).crm_id.email_from
        _logger.info("1111**************************************")
        print "Ref....................",ref_no
        # for fetch ip of user who do click on i agree
        if "HTTP_X_FORWARDED_FOR" in request.httprequest.environ:
            # Virtual host   
            ip = request.httprequest.environ["HTTP_X_FORWARDED_FOR"]
            _logger.debug(">>>>HTTP_X_FORWARDED_FOR>>>>>>>")
            _logger.info("2222**************************************")
            print "IPPPPPPPPPPPPPPPPPPPPP",ip
        elif "HTTP_HOST" in request.httprequest.environ:
            # Non-virtualhost
            ip = request.httprequest.environ["REMOTE_ADDR"]
            _logger.debug(">>>>HTTP_HOST>>>>>>>")
            _logger.info("3333**************************************")
            print "IPPPPPPPPPPPPPPPPPPPPP",ip
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
        job_id = request.env['job.description'].sudo().search([('name','=',ref_number)])
        c_name = job_id.jd_company
        comp_name = request.env['res.partner'].sudo().search([('name','=',c_name)])
        comp_name.write({'pre_sale_contacts':False,'post_sale_contacts':True}) #move to in customers and set post sales true after agree
        print 'Company Name',comp_name
        job_id.write({'agree': True,
            'jd_mail_from':mail,
            'ip_add_of_user':ip,
            'agree_name':agree_name})
        if job_id.agree:
            job_id.send_mail_templates() #send mails to smtp user and other on agree
            # job_id.active = False # transfer lead to post sales after agree
            # job_id.crm_id.to_be_post_sales = True # transfer lead to post sales after agree

        # if not job_id.agree:
        #     window = Tk()
        #     window.wm_withdraw()
        #     window.geometry("1x1+200+200")#remember its .geometry("WidthxHeight(+or-)X(+or-)Y")
        #     tkMessageBox.showerror(title="Warning",message="Ref number is not proper",parent=window)
        #     return request.render("indimedi_crm.page_action", {
        #        })
        return http.local_redirect("http://www.entigrity.com/payment/") #redirect payment link on  I agree click

    # @http.route(['/go_to_payment'], type='http', auth="public", website=True,)
    # def make_payment(self, **kw):
    #     print "\n==>BHOOMMM"
    #     return http.local_redirect("https://www.google.com/")
    
    
    