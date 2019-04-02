# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Ent Lead Signup',
    'version' : '1.0',
    'summary': 'Ent Lead Signup',
    'description': """
		Ent Lead Signup
		Module Help to manage odoo lead signup functionality
    """,
    'category': 'Sales',
    'website': 'https://www.entigrity.com',
    'images' : [],
    'depends' : [
		'crm',
		'indimedi_crm',
		'website',
	],
    'data': [
    	'views/ent_lead_signup_email_view.xml',
    ],
    'installable': True,
    'application': True,
}
