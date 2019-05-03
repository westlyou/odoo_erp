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
        'security/ent_lead_security.xml',
    	'data/lead_signup_email_data.xml',
    	'views/ent_lead_signup_email_view.xml',
    	'views/crm_lead_opportunity_view.xml',
    ],
    'installable': True,
    'application': True,
}
