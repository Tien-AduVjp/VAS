# -*- coding: utf-8 -*-
{
    'name': "Sales - Wallets",
    'name_vi_VN': "",

    'summary': """
Integrate Sales App and Wallet app""",

    'summary_vi_VN': """
Tích hợp ứng dụng Bán hàng và Ví điện tử
    	""",

    'description': """
Integrate Sales App and Wallet app

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tích hợp ứng dụng Bán hàng và Ví điện tử

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_wallet', 'sale'],

    # always loaded
    'data': [
        'security/module_security.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
