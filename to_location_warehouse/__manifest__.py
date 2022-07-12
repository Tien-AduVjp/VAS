# -*- coding: utf-8 -*-
{
    'name': "Stock Location's Warehouse Identification",
    'name_vi_VN': "Kho của địa điểm kho",
    'summary': """
Find the warehouse to which the location belongs""",
    'summary_vi_VN': """
Xác định kho mà địa điểm kho thuộc về""",

    'description': """
What it does
============
* By default, on the list view and form view of Stock Location, its warehouse is not displayed. This is difficult for user to select stock location in other applications (Sales, Purchase, etc.)
* Module ```to_location_warehouse``` helps user identify stock location's warehouse.

Key Features
============
After installing this module:

* Display *Warehouse* field on the form view of stock location.
* Display stock location's warehouse on the list view of stock location.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
* Mặc định trên giao diện danh sách (list view) và biểu mẫu (form view) Địa điểm kho không hiển thị Kho mà Địa điểm này thuộc về. Điều này gây khó khăn cho quá trình lựa chọn Địa điểm kho ở các ứng dụng khác như Mua hàng, Bán hàng, v.v. 
* Mô-đun ```to_location_warehouse``` giúp xác định được Kho của Địa điểm kho dễ dàng hơn.

Tính năng nổi bật
=================
Sau khi cài đặt mô-đun:

* Hiển thị trường *Kho hàng* trên giao diện biểu mẫu Địa điểm kho.
* Hiển thị Kho mà Địa điểm kho thuộc về ở giao diện danh sách Địa điểm kho.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],
    'data': [
        'views/stock_location_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
