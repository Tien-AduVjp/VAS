# -*- coding: utf-8 -*-
{
    'name': "Hide Enterprise Modules",
    'name_vi_VN': 'Ẩn Mô-đun trong ấn bản Enterprise',
    'summary': """
Do not bother Community Edition Users with Enterprise modules""",
    'summary_vi_VN': 'Hạn chế hiển thị các mô-đun ấn bản Enterprise với người dùng ấn bản Community',

    'description': """
What it does
============
- The name itself says what it does. This module is to hide Enterprise modules that are not available in your Odoo CE instance.
- Those modules will appear again either when they are available in your system or when you uninstall this module

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
- Mô-đun này giúp ẩn các mô-đun chỉ có trong ấn bản Enterprise mà không được sử dụng trong ấn bản Community.
- Các mô-đun bị ẩn đó sẽ xuất hiện trở lại trong trường hợp chúng có sẵn trong hệ thống của người dùng, hoặc khi người dùng gỡ cài đặt mô-đun này.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_module_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 4.5,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': "uninstall_hook",
}
