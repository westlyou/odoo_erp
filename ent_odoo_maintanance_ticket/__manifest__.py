# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Ent Odoo Maintanance',
    'version' : '1.0',
    'summary': 'Asset Management',
    'description': """
		Asset Management
    """,
    'category': 'Human Resources',
    'website': 'https://www.odoo.com/page/billing',
    'images' : [],
    'depends' : [
		'maintenance',
		'hr_maintenance',
	],
    'data': [
    	'views/maintenace_request_view.xml',
    ],
    'installable': True,
    'application': True,
}
