# -*- coding: utf-8 -*-

{
    'name': 'Mail cc bcc',
    'category': 'Discuss',
    'sequence': 25,
    'summary': 'Mailing Lists',
    'description': """Email Configuration with CC and Bcc""",
    'author': 'Indimedi Solutions Pvt. Ltd.',
    'website': 'http://www.indimedi.in',
    'depends': ['base', 'base_setup', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/mail_compose_message_view.xml',
        'views/mail_message_view.xml',
        'views/document_followers_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': False,
    'icon': "/indimedi_cc_bcc_mail/static/src/img/icon.png",
}
