{
    'name': "Account Reconciliation Widget",
    'name_vi_VN': "Đối soát kế toán",

    'summary': """
Account Reconciliation Widget and Functions for bank statement reconciliation and journal items reconciliation
""",
    'summary_vi_VN': """
Cung cấp tính năng đối soát các phát sinh kế toán, đối soát sao kê ngân hàng
""",

    'description': """
What it does
============

#. Restore bank reconciliation functionality which was removed from Odoo CE 14 and later
#. Track journal item's reconciliation date

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

#. Khôi phục lại tính năng đối soát đã bị gỡ bỏ ở Phiên bản Odoo 14, ấn bản Community
#. Theo vết ngày đối soát của các phát sinh kế toán dễ dàng hơn

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

""",

    'author': "Odoo S.A.,Viindoo",
    'maintainer': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_account_views.xml',
        'views/account_journal_dashboard_views.xml',
        'views/account_bank_statement_line_views.xml',
        'views/account_bank_statement_views.xml',
        'views/account_move_line_views.xml',
        'views/res_config_settings_views.xml',
        'views/assets.xml',
    ],
    'qweb': [
        "static/src/xml/account_reconciliation.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'images': [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'LGPL-3',
}
