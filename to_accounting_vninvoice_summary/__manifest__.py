# -*- coding: utf-8 -*-
{
    'name': "Accounting VN-invoice Summary",
    'name_vi_VN': "",

    'summary': """
Allows the option of issuing e-invoices VN-Invoice in a detailed or aggregated form""",

    'summary_vi_VN': """
cho phép tuỳ chọn xuất hoá đơn điện tử VN-Invoice theo mẫu chi tiết hoặc mẫu gộp
    	""",

    'description': """
What it does
============
Allows the option of issuing e-invoices VN-Invoice in a detailed or aggregated form

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
cho phép tuỳ chọn xuất hoá đơn điện tử VN-Invoice theo mẫu chi tiết hoặc mẫu gộp

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_accounting_vninvoice','to_einvoice_summary'],
    'images' : ['static/description/main_screenshot.png'],
    # always loaded

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
