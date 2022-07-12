{
    'name': "Reversed Invoice Line",
    'name_vi_VN': "Dòng hóa đơn đảo ngược",

    'summary': """Know refund lines being reversals of invoice lines of original invoices""",

    'summary_vi_VN': """Biết dòng hoàn trả là dòng đảo ngược của các dòng hóa đơn của hóa đơn gốc nào""",

    'description': """
What it does
============

This module allows to link refund lines with invoice lines of original invoices

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Phân hệ này cho phép liên kết các dòng hoàn tiền với các dòng hóa đơn gốc.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    'category': 'Accounting/Accounting',
    'version': '0.1',

    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
    ],
    'demo': [],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'post_init_hook': 'post_init_hook',
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
