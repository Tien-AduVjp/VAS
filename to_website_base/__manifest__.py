# -*- coding: utf-8 -*-
{
    'name': "TVTMA Website Base",
    'name_vi_VN': "Module website cơ sở", 
    'summary': """
Technical Base for TVTMA website applications""",
    'summary_vi_VN': """
Module Kĩ thuật Cở sở cho các Ứng dụng Web của TVTMA""",
    'description': """
Technical Base for TVTMA website applications
    """,
    'description_vi_VN': """
Module Kĩ thuật Cở sở cho các Ứng dụng Web của TVTMA""",

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'views/templates.xml',
        # 'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'sequence': 119,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
