# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Ent Dinner',
    'version' : '1.0',
    'summary': 'Dinner',
    'description': """
		Manage Dinner Order, Meal, Food
    """,
    'category': 'Human Resources',
    'website': 'https://www.odoo.com/page/billing',
    'images' : [],
    'depends' : [
		'lunch',
	],
    'data': [
    	'views/dinner_menu_view.xml',
    	'views/lunch_order_view.xml',
    ],
    'installable': True,
    'application': True,
}
