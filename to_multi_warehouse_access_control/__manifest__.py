# -*- coding: utf-8 -*-
{
    'name': "Multi Warehouse Access Control",
    'name_vi_VN': "Kiểm Soát Nhiều Quyền Truy Cập Kho",

    'summary': """
Multi level access control for every warehouse
        """,
    'summary_vi_VN': """
Kiểm soát quyền truy cập đa cấp cho mọi kho
        """,
    'description': """
Key Features
============
Multi level access control for every warehouse

* Inventory / Users: Own Documents

    * Can view and handle stock operations related to stock locations and warehouses that they have access rights

* Inventory / Warehouse Manager

    * Can view and handle ALL stock operations related to stock locations and warehouses that they have access rights

* Inventory / All Warehouses Manager

    * Can view and handle ALL stock operations

* Inventory / Manager

    * Can do everything in the Inventory application

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Kiểm soát quyền truy cập đa cấp cho mọi kho

* Kiểm kho / người dùng: Chỉ tài liệu chính mình

    * Có thể xem và xử lý hoạt động kho liên quan đến địa điểm kho và kho mà họ có quyền truy cập

* Kiểm kho / Quản lý kho

    * Có thể xem và xử lý tất cả hoạt động kho liên quan đến địa điểm kho và kho mà họ có quyền truy cập

* Kiểm kho / Tất cả quản lý kho

    * Có thể xem và xử lý tất cả hoạt động kho

* Kiểm kho / Quản lý

    * Có thể làm mọi thứ trong ứng dụng Kiểm kho

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Warehouse',
    'version': '1.0.1',

    'depends': ['to_location_warehouse', 'delivery', 'to_stock_account_moves_link'],

    'data': [
        'data/stock_config_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/stock_warehouse_view.xml',
        'views/stock_location_view.xml',
        'views/product_view.xml',
        'views/stock_menu_view.xml',
        'views/stock_inventory_view.xml',
        'views/stock_picking_view.xml'
    ],
    'images' : [
        'static/description/main_screenshot.png',
        ],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
