# -*- coding: utf-8 -*-
{
    'name': "Repair Order from Maintenance Request",
    'name_vi_VN': "Lệnh Sửa Chữa Từ Yêu Cầu Bảo Trì",
    'summary': """Generate repair order from equipment maintenance request.
        """,

    'summary_vi_VN': """
Tạo lệnh sửa chữa từ yêu cầu bảo trì thiết bị.
        """,

    'description': """
What it does
============
This module helps create Repair order from Maintenance request

* Add the button "Create repair order" on Maintenance request form
* Show the list of repair orders related to maintenance requirements

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này cho phép tạo Lệnh sửa chữa từ Yêu cầu bảo trì

* Thêm nút hành động "Tạo lệnh sửa chữa" trên form Yêu cầu bảo trì.
* Thống kê danh sách lệnh sửa chữa liên quan đến yêu cầu bảo trì.

Ấn bản được Hỗ trợ
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
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_equipment', 'viin_repair'],

    # always loaded
    'data': [
        'views/maintenance_request_view.xml',
        'views/repair_order_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
