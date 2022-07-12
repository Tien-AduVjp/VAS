# -*- coding: utf-8 -*-
{
    'name': "[TEST] Test Drop Shipping",
    'name_vi_VN': "",
    'summary': """
Run test of module stock_dropshipping
    """,
    'summary_vi_VN': """
    """,
    'description': """
The Problem
===========
When run test of stock_dropshipping, there is test case test_lifoprice, which can't be passed due to group_stock_multi_locations is enabled.
In this case, the field quantity_done on stock move form is not editable, and we can's set value for it in form.


What it does
============
This module will overwrite and re-run test of stock_dropshipping.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Đặt vấn đề
==========

Module này làm gì
=================

Ấn bản được Hỗ trợ
==================
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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_dropshipping'],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
