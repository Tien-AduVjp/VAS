# -*- coding: utf-8 -*-
{
    'name': "Odoo Apps Sales",
    'name_vi_VN': 'Bán ứng dụng Odoo',
    'summary': "Sell your Odoo Apps and allow customer downloads from the portal",
    'summary_vi_VN': 'Bán ứng dụng Odoo của bạn và cho phép khách hàng tải xuống từ cổng thông tin',

    'description': """
What it does
============
This module helps you sell your Odoo apps. When your customer's done the payment, she/he will able to download the applications from her/his portal.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này cho phép bạn bán ứng dụng Odoo. Khi khách hàng của bạn thanh toán xong, họ có thể vào giao diện portal của họ để tải xuống ứng dụng đó.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Odoo Apps',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_product_license_sale', 'to_odoo_module'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_templates.xml',
        'report/sale_report_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
