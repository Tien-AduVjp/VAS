# -*- coding: utf-8 -*-

{
    'name': "Partner Info on Lot/Serial",
    'old_technical_name': ' to_stock_production_lot_partner_infor',
    'name_vi_VN': 'Thông tin đối tác cho từng Số Lô / Serial',
    'summary': """
Provide Customer / Vendor info on a Lot/Serial""",

    'summary_vi_VN': """
Thêm thông tin khách hàng, nhà cung cấp và vùng sử dụng thiết bị cho từng Số Lô / Serial""",

    'description': """
What it does
============
Usually, businesses providing warranty and maintenance services for equipments (for example, boat engines, cars, tractors, etc.)
have needs to store and control information about Customers, Suppliers and Area/Region of use in which the device is being operated
(Service State) to serve some advertising campaigns, after-sales customer care. Example: Carrying out a free maintenance and
maintenance campaign for one or several engines and equipment of the company in a region/province/city.

This module adds the following fields to Lot/Serial:

* Customer
* Vendor
* Service State

Key Features
============

* When the product is delivered, if the Destination Location is the Customer Location type, the customer name and service state will be
  updated when the transfer is confirmed.
* When the product is received, if the Source Location is the Vendor Location type, the Vendor Name will be updated when the transfer
  is confirmed.
* Update names of Supplier and Customer on the Serial number management if the product's route is Dropshipping type.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thông thường, các doanh nghiệp làm dịch vụ bảo hành, bảo trì các thiết bị (Ví dụ như động cơ tàu thuyền, oto, đầu kéo....)
có nhu cầu kiểm soát, lưu thông tin Khách hàng, Nhà cung cấp và Vùng/Miền sử dụng mà thiết bị đang được vận hành
(Tỉnh/Thành Phục vụ) để phục vụ một số chiến dịch quảng bá, chăm sóc Khách hàng sau bán. Ví dụ: Thực hiện chiến dịch bảo trì,
bảo dưỡng miễn phí cho một hoặc một vài động cơ, thiết bị của hãng ở một Tỉnh/Thành, một khu vực.

Mô đun này cho phép thêm thông tin Khách hàng, Nhà cung cấp và Tỉnh/Thành Phục vụ vào Số Lot/Sê-ri.

Tính năng chính
===============
* Khi sản phẩm xuất kho, nếu Địa điểm đích là kiểu Địa điểm khách hàng thì khi xác nhận dịch chuyển sẽ cập nhật Tên khách hàng
  và vùng sử dụng sản phẩm
* Khi sản phẩm nhập kho, nếu Địa điểm nguồn là kiểu Địa điểm nhà cung cấp thì khi xác nhận dịch chuyển sẽ cập nhật Tên nhà cung cấp
* Nếu tuyến của sản phẩm là Dropshipping, cập nhật tên Nhà cung cấp và Tên khách hàng trên quản lý số Lot/Sê-ri.

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
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Inventory',
    'version': '0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['stock'],
    
    # always loaded
    'data': [
        'views/stock_production_lot_views.xml',
        'views/res_partner_views.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
