# -*- coding: utf-8 -*-
{
    'name': "Vietnam Bank Payment Icons",
    'name_vi_VN': "Logo Thanh toán Ngân hàng ở Vietnam",

    'summary': """
Payment Icons for banks in Vietnam""",

    'summary_vi_VN': """
Cung cấp các biểu tượng/logo cho thanh toán qua các ngân hàng ở Việt Nam
    	""",

    'description': """
What it does
============
Technical module to provide Payment Icons for banks in Vietnam for other payment_* module to reuse

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Đây là một module kỹ thuật cung cấp các biểu tượng ngân hàng phục vụ cho các module thanh toán trực tuyến có thể tái sử dụng.

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
    # Check https://github.com/tvtma/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['payment'],

    # always loaded
    'data': [
        'data/payment_icon_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
