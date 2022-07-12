# -*- coding: utf-8 -*-
{
    'name': "VAT Counterpart Account",
    'name_vi_VN': "Tài Khoản Đối Ứng Thuế GTGT",

    'summary': """Add Counterpart Account into Tax form for VAT""",
    'summary_vi_VN': """Thêm tài khoản đối ứng vào form Thuế cho thuế GTGT""",
    'description': """
Key Features
============
In some use cases where we do not have a counterpart account for a tax entry, this module add Counterpart Account declaration on Tax form to solve the issue.

For example, according to Vietnam Accounting Standards, the account code 33312 (VAT on imported goods) requires the account 1331 (VAT on purchase of goods and services) for a counterpart of its.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
Trong một số trường hợp khi chúng ta không có tài khoản đối ứng cho mục thuế, module này thêm tài khoản đối ứng vào form thuế để giải quyết vấn đề này.

Ví dụ, trong Kế toán Việt Nam, khi hạch toán thuế GTGT hàng nhập khẩu vào tài khoản 33312 (GTGT Hàng nhập) thì cần đối ứng với 1331 (GTGT được khấu trừ) cho tài khoản đối ứng.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_tax_is_vat', 'viin_account'],

    # always loaded
    'data': [
        'views/account_tax_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
