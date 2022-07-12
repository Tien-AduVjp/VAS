# -*- coding: utf-8 -*-
{
    'name': "Accounting VN-invoice Summary",
    'old_technical_name': 'to_accounting_vninvoice_summary',

    'name_vi_VN': "Gộp dòng hóa đơn điện tử VN-invoice",

    'summary': """
Allows the option of issuing e-invoices VN-Invoice in a detailed or aggregated form""",

    'summary_vi_VN': """
Cho phép tuỳ chọn xuất hoá đơn điện tử VN-Invoice theo mẫu chi tiết hoặc mẫu gộp
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
Cho phép tuỳ chọn xuất hoá đơn điện tử VN-Invoice theo mẫu chi tiết hoặc mẫu gộp

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

    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_l10n_vn_accounting_vninvoice','l10n_vn_edi_summary'],
    'images' : ['static/description/main_screenshot.png'],
    # always loaded

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
