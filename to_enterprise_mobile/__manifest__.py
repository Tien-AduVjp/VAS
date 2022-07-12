# -*- coding: utf-8 -*-
{
    'name': "Enterprise Mobile",

    'summary': """
Odoo EE Mobile App support for Odoo CE""",

    'description': """
Odoo Mobile App does not support Odoo CE. This module provide a bypass so that the app can support Odoo CE
    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
#         'views/views.xml',
#         'views/templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
