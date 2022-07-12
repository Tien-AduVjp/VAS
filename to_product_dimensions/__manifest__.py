# -*- coding: utf-8 -*-

{
    'name' : 'Product Dimensions',
    'name_vi_VN': 'Kích thước sản phẩm',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Manage Product Dimensions for products and product variants',
    'summary_vi_VN': 'Quản lý kích thước của sản phẩm và biến thể',
    'sequence': 24,
    'category': 'Sales',
    'description':"""

What it does
============
- This module is built for other applications to extend. For example, the application *Fleet Stock Picking (to_fleet_stock_picking)* depends on this application to make sure the goods loaded on a vehicle (for transportation) do not exceed the maximum allowed volume/ weight.

Key Features
============
1. This application allows users to declare dimensions (i.e. Width, Height, Length) and the Stowage Factor (SF) on the product form view. In case all those 3 dimensions are input, the value of the volume field will be computed automatically according to the dimensions input.
2. The dimensions are available for both Products and Product Variants.
3. Each product has a switch to allow you to enable *Dimensions in Name* feature for the product

Notes
=====
* The dimensions and Stowage Volume fields are visibly ONLY when the product type is either Stockable or Consumable

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Mô-đun này được xây dựng để mở rộng các ứng dụng khác. Ví dụ, ứng dụng *Nhận hàng cho đội phương tiện (to_fleet_stock_picking)* phụ thuộc vào mô-đun này để kiểm tra xem hàng hóa chất lên xe vận chuyển có vượt quá khối lượng/ trọng lượng tối đa cho phép hay không.

Tính năng nổi bật
=================
1. Cho phép người dùng nhập kích thước (Chiều rộng, Chiều cao, Chiều dài) và Hệ số chất xếp (SF) cho sản phẩm trong ứng dụng *Kho vận*. Giá trị của trường thể tích sẽ được tính tự động theo 3 kích thước đã nhập.
2. Cho phép người dùng nhập kích thước cho cả Sản phẩm và Biến thể sản phẩm.
3. Mỗi sản phẩm có một nút chọn, cho phép người dùng bật tính năng *Nối Kích thước vào Tên* cho sản phẩm 

Thông tin thêm
==============
* Các trường Kích thước và Thể tích chất xếp CHỈ hiển thị đối với sản phẩm Tiêu dùng hoặc Có thể lưu kho

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['stock'],
    'data': [
        'data/decimal_precision.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
