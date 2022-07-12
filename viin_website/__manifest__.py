# -*- coding: utf-8 -*-

{
    'name': 'Viin Website',
    'name_vi_VN': "",

    'summary': 'Enhanced features for website',
    'summary_vi_VN': """
Các tính năng cao cấp cho ứng dụng website
""",

    'description': """
What it does
============
This module offers more enhanced and advanced features for website app

Key Features
============
- Replace website applications dropdown menu with a toggle menu that will redirect user to backoffice applications
- More features will be added day by day...

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Module này cải tiến các tính năng sẵn có và thêm các tính năng cao cấp cho website

Tính năng nổi bật
=================
- Thay thế menu xổ xuống của ứng dụng website bằng menu chuyển đổi để chuyển hướng người dùng đến các ứng dụng trong backofffice
- Các tính năng khác sẽ được bổ sung dần...

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['website'],
    'data': [
        'views/asset_frontend.xml',
        'views/templates.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
