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


_logger = logging.getLogger(__name__)
    

class AgreementConfirm(http.Controller):
    @http.route('/agreement_confirm/<agreement>/<token>', type='http', auth='public', website=True)
    def agreement_confirm(self, agreement, token, **post):
        data = {}
        job_id = request.env['job.description'].search([('id', '=', agreement),('random_token', '=', token)])
        
        if job_id.agree:
            return request.render('indimedi_crm.already_agreed', data)
        
        if not job_id:
            return request.render('indimedi_crm.i_agree_form', {'error': "Invalid Agreement Access Token!"})
        data = {'agreement': agreement, 'token': token}
        return request.render('indimedi_crm.i_agree_form', data)
    
    @http.route('/agreement_done/<agreement>/<token>', type='http', auth='public', website=True)
    def agreement_yes(self, agreement, token, **post):
        data = {}
        ip = request.httprequest.environ["REMOTE_ADDR"]
#         ip = request.httprequest.remote_addr
        
        print"===============================",ip 
        agent = request.httprequest.environ.get('HTTP_USER_AGENT')
        browser = httpagentparser.detect(agent)
        print"browser=================================",browser
        
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
        
        agreement_id.sudo().write({'agree': True,
                                   'ip_add_of_user': ip,
                                   'ip_info': ip_info})
        
        if agreement:
            data = {'agreement': agreement}
        return request.render('indimedi_crm.i_agree', data)
    
    
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
    
    
    