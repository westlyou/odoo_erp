# -*- coding: utf-8 -*-
{
    'name': 'Web Digital Signature v10.0',
    'version': '10.0.1.0.0',
    'author': 'Indimedi Solutions Pvt. Ltd.',
    'maintainer': 'Indimedi Solutions Pvt. Ltd.',
    'category': '',
    'complexity': 'easy',
    'depends': ['web'],
    'summary': 'Digital signature control',
    'description': '''
     This module provides the functionality to store digital signature
     for a record.
        -> This  module is helpful to make your business process a little
           bit more faster & makes it more user friendly by providing you
           digital signature functionality on your documents.
        -> It is touch screen enable so user can add signature with touch
           devices.
        -> Digital signature can be very usefull for documents such as
           sale orders, purchase orders, inovoices, payslips, procurement
           receipts, etc.
        The example can be seen into the User's form view where we have
        added a test field under signature.
    ''',
    'data': [
        'views/we_digital_sign_view.xml',
        'views/users_view.xml'],
    'website': 'http://www.serpentcs.com',
    'qweb': ['static/src/xml/digital_sign.xml'],
    'installable': True,
    'auto_install': False,
}
