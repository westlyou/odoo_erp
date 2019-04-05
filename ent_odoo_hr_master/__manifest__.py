# -*- coding: utf-8 -*-

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
		'indimedi_crm',
	],
    'data': [
    	'data/emp_sequence_data_view.xml',
    	'security/ir.model.access.csv',
    	'views/hr_employee.xml',
    ],
    'installable': True,
    'application': True,
}
