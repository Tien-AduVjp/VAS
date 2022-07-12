# -*- coding: utf-8 -*-
{
    'name': "Currency Conversion Difference Move for Payment Transaction",
    'name_vi_VN': "Quy đổi và làm tròn cho giao dịch thanh toán",

    'summary': """
Currency Conversion Difference Move for Payment Transactions that have currency other than their corresponding payment's""",

    'summary_vi_VN': """
Tạo bút toán chênh lệch do quy đổi và làm tròn, cho thanh toán mà có tiền tệ khác với tiền tệ của giao dịch thanh toán tương ứng của nó
        """,

    'description': """
Currency Conversion Difference Move for Payment Transactions that have currency other than their corresponding payment's

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tạo bút toán chênh lệch do quy đổi và làm tròn, cho thanh toán mà có tiền tệ khác với tiền tệ của giao dịch thanh toán tương ứng của nó

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
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/payment_acquirer_views.xml',
        'views/res_config_views.xml',
    ],

    'images' : [
        'static/description/main_screenshot.png'
        ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
