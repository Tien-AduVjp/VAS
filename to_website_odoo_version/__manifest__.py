# -*- coding: utf-8 -*-
{
    'name': "Website Odoo Version",
    'name_vi_VN': "",

    'summary': """
Technical module to integrates Odoo Version and Website""",
    'summary_vi_VN': 'Module kĩ thuật để tích hợp Phiên bản Odoo vào Website',
    'description': """
What is does
============
This is a technical module that provides technical helps for features related to Odoo versions and websites. It does nothing visually.

Key Features
============
- Update the description of different Odoo versions
- Show the differences among versions

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Đây là một module kĩ thuật chủ yếu cung cấp các trợ giúp kĩ thuật cho tính năng liên quan đến Phiên bản Odoo và websites.

Tính năng nổi bật
=================
- Cập nhật phần mô tả cho các phiên bản Odoo khác nhau
- Phân biệt sự khác nhau giữa các phiên bản.

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
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'to_odoo_version'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/odoo_version_views.xml',
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
