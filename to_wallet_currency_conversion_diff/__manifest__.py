# -*- coding: utf-8 -*-
{
    'name': "Currency Conversion Difference Move for Wallet Payment Transaction",
    'name_vi_VN': "Quy đổi và làm tròn tiền tệ cho giao dịch ví điện tử",

    'summary': """
Enable currency conversion difference move for wallet payment transaction""",

    'summary_vi_VN': """
Hỗ trợ quy đổi và làm tròn tiền tệ cho giao dịch ví điện tử""",

    'description': """

Key features
============
    
This module integrates "to_currency_conversion_diff" module with "to_wallet" module, that helps:

    * Allow to make currency exchange from VND to foreign currency and vice versa to enable payment on payment acquires
    * Creat rounding entry for the currency conversion difference in ewallet payment transaction
    
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Tính năng nổi bật
==================

Mô-đun này tích hợp hai module "to_currency_conversion_diff" và "to_wallet", giúp thực hiện:

    * Quy đổi tiền tệ từ VND sang ngoại tệ hoặc ngược lại để thực hiện thanh toán trên các cổng thanh toán điện tử
    * Tạo bút toán làm tròn các chênh lệch do quy đổi tiền tệ trong các giao dịch ví điện tử

Ấn bản được hỗ trợ
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
    'depends': ['to_wallet', 'to_currency_conversion_diff'],

    # always loaded
    'data': [
    ],

    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
