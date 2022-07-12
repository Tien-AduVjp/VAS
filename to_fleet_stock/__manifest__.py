# -*- coding: utf-8 -*-
{
    'name': "Fleet Stock Consumption",
    'name_vi_VN': 'Xuất Kho Tiêu Thụ Cho Đội Phương Tiện',
    'summary': """
Record stock moves with vehicle reference""",
    'summary_vi_VN': """
Tham chiếu dịch chuyển kho với phương tiện""",
    'description': """
This application integrates the Odoo's Fleet Management application and Inventory to support stock consumption management for your fleet

Key Features
============
1. New Stock Operation Type: Fleet Consumption
2. Record stock consumption (parts, fuel, etc) for your Fleet with Stock Moves as other stock operation
3. Auto generates a vehicle cost if the corresponding stock move moves to a production location that present your vehicles.
4. Keep track of stock that have been consumed for each vehicle

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này tích hợp ứng dụng Quản lý Đội phương tiện và Kho hàng của Odoo để hỗ trợ quản lý xuất kho tiêu thụ cho đội phương tiện của bạn

Tính năng chính
===============
1. Loại hoạt động kho mới: Tiêu thụ cho Đội phương tiện
2. Ghi lại xuất kho tiêu thụ (bộ phận, nhiên liệu, v.v.) cho Đội phương tiện của bạn với Dịch chuyển Kho, cũng như các hoạt động kho khác
3. Tự động tạo ra một chi phí của phương tiện nếu có một dịch chuyển kho tới địa điểm sản xuất tương ứng với phương tiện.
4. Theo dõi kho mà đã được tiêu thụ cho mỗi phương tiện

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['viin_fleet', 'stock_account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/stock_data.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_views.xml',
        'views/fleet_vehicle_log_services_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
