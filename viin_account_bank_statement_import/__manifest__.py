# -*- encoding: utf-8 -*-

{
    'name': 'Account Bank Statement Import',
    'name_vi_VN': 'Nhập sao kê ngân hàng',
    'summary': """Import bank statements in CSV and XLSX""",
    'summary_vi_VN': """Nhập liệu sao kê ngân hàng định dạng CSV and XLSX""",
    'description': """
Generic Wizard to Import Bank Statements For Odoo CE as this feature was removed since Odoo 14.

Key Features
------------

#. .CSV format (Comma Separated Values)
#. .XLSX  format (Excel)
#. ready for other to extends to support more formats

Editions Support
----------------
1. Community Edition

""",
'description_vi_VN': """
Cung cấp đồ thuật để nhập liệu sao kê ngân hàng

#. định dạng CSV (Comma Separated Values)
#. định dạng XLSX (Excel)
#. sẵn sàng cho các module khác mở rộng để hỗ trợ thêm các định dạng khác

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

""",
    'depends': ['viin_account_reconciliation'],
    'author': 'Viindoo,Odoo SA',
    'maintainer': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'version': '2.4.0',
    'category': 'Accounting/Accounting',

    'data': [
        'security/ir.model.access.csv',
        'wizard/journal_creation.xml',
        'views/account_bank_statement_import_view.xml',
        'views/account_bank_statement_import_templates.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/main_screenshot.png',
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
