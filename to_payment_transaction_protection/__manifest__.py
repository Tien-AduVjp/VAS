{
    'name': "Payment Transaction Protection",
    'name_vi_VN': 'Bảo vệ giao dịch thanh toán',
    'summary': 'Payment Transaction Protection',
    'summary_vi_VN': 'Bảo vệ giao dịch thanh toán',
    'description': """
What it does
============
Do not allow deletion of a payment transaction if it is still referred by a payment.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Không cho phép xoá giao dịch thanh toán nếu nó có liên kết đến một khoản thanh toán.

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment'],

    # always loaded
    'data': [
    ],
    'qweb': [
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
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
