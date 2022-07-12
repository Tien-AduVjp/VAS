{
    'name': 'Print Journal Entries',
    'name_vi_VN': 'In Phiếu Kế toán',

    'summary': 'Print Journal Entries in PDF',
    'summary_vi_VN': 'In phiếu Kế toán theo định dạng PDF',

    'version': '0.1.0',
    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Accounting/Accounting',
    'description': """
What it does
============
This module allows to print Journal Entries in PDF

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cho phép in phiếu kế toán theo định dạng PDF

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'depends': ['to_vietnamese_number2words', 'l10n_vn_common'],
    'data': [
          'views/report_account_move.xml',
          'views/report.xml',
      ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 27.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
