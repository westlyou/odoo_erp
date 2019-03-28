# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Ent Odoo HR Master',
    'version' : '1.0',
    'summary': 'Odoo HR Master',
    'description': """
		Asset Management
    """,
    'category': 'Human Resources',
    'website': 'https://www.entigrity.com',
    'images' : [],
    'depends' : [
		'hr',
	],
    'data': [
    	'views/hr_employee.xml',
    ],
    'installable': True,
    'application': True,
}
