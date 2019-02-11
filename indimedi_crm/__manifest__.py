# -*- coding: utf-8 -*-

{
    'name': 'Indimedi CRM',
    'version': '10.0.1.0.0',
    'author': 'Indimedi Solutions Pvt. Ltd.',
    'maintainer': 'Indimedi Solutions Pvt. Ltd.',
    'category': 'Sales',
    'complexity': 'easy',
    'depends': ['base', 'crm', 'project', 'calendar', 'sale_crm', 'mail', 'sale',
                'hr_timesheet', 'web', 'indimedi_cc_bcc_mail',
                'web_readonly_bypass'],
    'summary': 'Leads, Opportunities, Activities',
    'description': '''
    This Module contains the custom crm and contact module functionalities
    ''',
    'data': [
             'security/project_security.xml',
             'security/invoice_security.xml',
             'security/holidays_security.xml',
             'security/ir.model.access.csv',
             'data/website_templates.xml',
             'data/agreement.xml',
             'data/payment_view.xml',
             'data/mail_template_agreement_one.xml',
             'data/mail_template_agreement_two.xml',
             'data/mail_template_agreement_three.xml',
             'data/mail_template_agreement_four.xml',
             'data/submit_mail.xml',
             'data/crm_master_demo_data.xml',
             'data/seq_job_agreement.xml',
             'data/agreement_invoicing.xml',
             'data/auth_signup_data.xml',
             'data/calendar_data.xml',
             # 'data/timesheet_send.xml',
             'data/resume_post_sales.xml',
             'data/timesheet_template.xml',
             'data/post_sale_resume.xml',
             'data/invoice_schedular.xml',
             'data/mail_data.xml',
             'views/crm_lead_views.xml',
             'views/calender_views.xml',
             'views/sale_views.xml',
             'views/contacts_view.xml',
             'views/web_calendar_templates.xml',
             'views/agreement_view.xml',
             'views/hr_employee.xml',
             'views/project_views.xml',
             'wizard/time_sheet_wizard.xml',
             'views/report_timesheet_templates.xml',
             'views/preferences.xml',
             'views/public_holiday_view.xml',
             'views/report_timesheet_invoice.xml',
             'data/analysis_timesheet_sent.xml',
             'views/invoice_views.xml',
             'views/hide_menus_customer.xml',
             
            #new file added
            'wizard/change_billing_info_wizard.xml',
            'views/project_leave_view.xml',
            'data/project_leave_email.xml',
            'security/meeting_security.xml',
        ],
    'qweb': [
        'static/lib/web_calendar/xml/*.xml',
    ],
    'website': 'http://www.indimedi.in',
    'installable': True,
    'auto_install': False,
}