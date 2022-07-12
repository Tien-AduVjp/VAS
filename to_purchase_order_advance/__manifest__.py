{
    'name': "Purchase Advance Payment",
    'name_vi_VN': 'Tạm ứng Mua hàng',

    'summary': """
Allows users to make advance payments for purchase order.
""",
    'summary_vi_VN': """
Cho phép tạo các khoản tạm ứng cho đơn mua hàng.
""",

    'description': """

This module allow linking from payment to purchase order, and make that payment only reconcilable for invoices of it's linked order.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô-đun này cho phép tạo liên kết từ thanh toán đến đơn mua hàng. Thanh toán đó sẽ chỉ được dùng để đối soát với hoá đơn của đơn hàng đã liên kết.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase', 'viin_account_reconciliation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_view.xml',
        'wizards/assign_to_invoice_wizard_views.xml',
        'wizards/add_po_to_payment_wizard_views.xml',
        'views/account_payment_view.xml',
        'views/assets.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': [
        'static/src/xml/account_reconciliation.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
