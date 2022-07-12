# -*- coding: utf-8 -*-
{
    'name': "Counterpart Account Reports",
    'name_vi_VN': "Báo Cáo Đối Ứng Tài Khoản",
    'summary': """
Accounting Reports with counterpart support""",
    'summary_vi_VN': """
Hỗ trợ Báo cáo Kế toán với đối ứng""",
    'description': """
What it does
============
Accounting Reports with counterpart support

Editions Supported
==================
1. Community Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Hỗ trợ Báo cáo Kế toán với đối ứng

Ấn bản được hỗ trợ
==================
1. Ấn bản Community

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_account_counterpart'],

    # always loaded
    'data': [
        'views/report_overdue.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
