{
    'name': "Sale Advance Payment",
    'name_vi_VN': 'Tạm ứng Bán hàng',

    'summary': """
Allows users to make advance payments for sale order.
""",
    'summary_vi_VN': """
Cho phép tạo các khoản tạm ứng cho đơn bán hàng.
""",

    'description': """
What it does
============
This module allows linking from payments to sales orders. The payment will only be used to reconcile the invoice of the linked order.

Key Features
============
* Allows linking from payments to sales orders.
* When reconciling payments with invoices, give a warning if the payment and invoice are not linked to the same sales order
* Can only be used to reconcile invoices associated with that order

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này cho phép tạo liên kết từ thanh toán đến đơn bán hàng. Thanh toán đó sẽ chỉ được dùng để đối soát với hoá đơn của đơn hàng đã liên kết.

Tính năng nổi bật
=================
* Cho phép tạo liên kết từ thanh toán đến đơn bán hàng.
* Khi đối soát thanh toán với hóa đơn, đưa ra cảnh báo nếu khoản thanh toán và hóa đơn không cùng liên kết với cùng một đơn hàng bán
* Chỉ được dùng để đối soát với những hóa đơn có liên kết với đơn hàng đó

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

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
    'depends': ['sale', 'viin_account_reconciliation'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'wizards/assign_to_invoice_wizard_views.xml',
        'wizards/add_so_to_payment_wizard_views.xml',
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
