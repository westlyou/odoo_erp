# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Entigrity HR Recruitment Process',
    'version' : '1.0',
    'summary': 'Entigrity Recruitment Process',
    'description': """
		Entigrity Recruitment Process
    """,
    'category': 'Sales',
    'website': 'https://www.entigrity.com',
    'images' : [],
    'depends' : [
		'hr_recruitment',
	],
    'data': [
    	'data/hr_applicant_data.xml',
    	'views/hr_applicant_view.xml',
    	'views/edu_detail_view.xml',
    	'views/web_hr_applicant_template_view.xml',
    ],
    'installable': True,
    'application': True,
}
