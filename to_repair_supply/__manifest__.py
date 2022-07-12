# -*- coding: utf-8 -*-
{
    'name': "Repair Supply Chain",
    'old_technical_name': 'to_mrp_repair_supply',
    'name_vi_VN': "Chuỗi Cung Ứng Sửa Chữa",
    'summary': """
Manage a full supply chain for repair services
        """,
    'summary_vi_VN': """
Quản lý toàn bộ chuỗi cung ứng cho dịch vụ sửa chữa""",
    'description': """
What it does
============

This module allows you to manage a full supply chain for repair services.

* Allow to choose Current Location of Product to repair and Parts, instead of only Repair location as default
* Create product moves to supply for a Repair order. For example:

  * A Repair order is created, there are stock moves such as:

    * Product to repair: From Current location (Customer Location) to Repair location
    * Parts for repair order: From Current location (Internal location, Vendor location) to Repair location.
      In case of insufficient quantity, there are stock moves to fulfill the demand.

  * When the Repair order got done, there would be a delivery of the Product to repair from Repair location to the initial
    location (Current location)
  * When the Repair order got cancelled, there would be a delivery of the Product to repair and Parts from Repair location
    to the initial location (Current location)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================

Mô-đun này giúp bạn quản lý toàn bộ chuỗi cung ứng cho dịch vụ sửa chữa.

* Cho phép lựa chọn Địa điểm hiện tại của Thiết bị cần sửa và phụ tùng cần dùng cho lệnh sửa chữa,
  thay vì chỉ quản lý Địa điểm sửa chữa như mặc định
* Tạo ra các dịch chuyển cần thiết để đáp ứng cho một lệnh sửa chữa. Ví dụ:

  * Khi có lệnh sửa chữa, hệ thống sẽ tạo ra các dịch chuyển:

    * Đưa Thiết bị cần sửa từ Địa điểm hiện tại (có thể là địa điểm khách hàng) đến Địa điểm sửa chữa
    * Đưa Phụ tùng từ Địa điểm Hiện tại (có thể là nơi lưu kho, hoặc địa điểm nhà cung cấp) đến Địa điểm Sửa chữa.
      Nếu thiếu phụ tùng, có thể tạo dịch chuyển để cung ứng đủ số lượng

  * Khi sửa chữa xong, hệ thống sẽ tạo ra dịch chuyển trả thiết bị về địa điểm ban đầu (Địa điểm hiện tại)
  * Khi hủy Lệnh sửa chữa, hệ thống sẽ tạo ra dịch chuyển để trả phụ tùng về kho, trả thiết bị cho khách

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Manufacturing',
    'version': '0.3',

    'depends': ['viin_repair', 'to_repair_access_group'],

    'data': [
        'data/picking_type.xml',
        'wizard/wizard_repair_request_supply_views.xml',
        'wizard/wizard_repair_order_consumption_views.xml',
        'wizard/wizard_repair_order_confirm_consumption_views.xml',
        'views/repair_order_views.xml',
        'views/stock_picking_views.xml',
        'wizard/stock_warn_insufficient_qty_views.xml',
        'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
