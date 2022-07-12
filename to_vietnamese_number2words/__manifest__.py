# -*- coding: utf-8 -*-
{
    'name': "Number to Vietnamese Words",
    'name_vi_VN' : "Chuyển đổi số sang chữ tiếng Việt",

    'summary': """
Convert from number to Vietnamese words""",
    'summary_vi_VN': """
Chuyển đổi số sang chữ tiếng Việt""",

    'description': """
Based Module for others to extend for conversion from number to Vietnamese words. This module will not do anything without its extensions

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô-đun cơ sở cho các mô-đun khác kế thừa để chuyển đổi từ số sang từ tiếng Việt. Mô-đun này sẽ không làm được gì nếu không có các phần mở rộng của nó

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
