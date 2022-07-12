# -*- coding: utf-8 -*-
{
    'name': "Odoo Versions Management",
    'name_vi_VN' : 'Quản lý phiên bản Odoo',
    'summary': "Manage Odoo versions and their parameters",
    'summary_vi_VN': 'Quản lý phiên bản Odoo và các thông số liên quan',
    'description': """
What it does
============
This module allows you to manage and define Odoo versions in your Odoo instance. This module is aimed for others to extend

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Mô tả
=====
Mô-đun này cho phép quản lý và khai báo các phiên bản Odoo trong hệ thống của bạn, đồng thời hỗ trợ tích hợp mở rộng với các mô-đun khác.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': ['to_config_management'],

    # always loaded
    'data': [
        'data/odoo_version_data.xml',
        'data/config_section_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_version_config_from_file_views.xml',
        'views/odoo_version_config_views.xml',
        'views/odoo_version_views.xml',
        'views/config_section_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
