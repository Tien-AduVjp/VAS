# -*- coding: utf-8 -*-
{
    'name': "Product's Cost Access",
    'name_vi_VN': "Truy cập Giá vốn Sản phẩm",

    'summary': """Restrict access to product's Cost field
       """,
    'summary_vi_VN': """Hạn chế truy cập đến trường Giá vốn của sản phẩm 
    """,

    'description': """
What it does
============
* By default, users who are authorized to view Products can see the Cost field on the Product form view.
* However, that information should not be shared to all users, because it also affects the pricing policy and business strategy of the Enterprise.
* The ```to_product_standard_price_access``` module will restrict users from accessing the product's Cost field.

Key Features
============
* This module creates a new access group named "Product Standard Price Access" and grants the group access to the field Cost on the product form & tree view.
* In other words, after installing this module, only users that are granted into the group "Product Standard Price Access" can see the Cost field on the product form & tree view.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Theo mặc định, những người dùng được cấp quyền vào xem Sản phẩm đều thấy được trường Giá vốn trên form Sản phẩm.
* Tuy nhiên, không phải tất cả người dùng thấy được thông tin đó đều tốt vì nó còn ảnh hưởng đến chính sách giá và chiến lược kinh doanh của Doanh nghiệp.
* Mô-đun ```to_product_standard_price_access``` sẽ hạn chế người dùng truy cập đến trường Giá vốn của sản phẩm.

Tính năng nổi bật
=================

* Sau khi cài đặt, mô-đun này sẽ tạo mới nhóm "Truy Cập Giá Tiêu Chuẩn Sản Phẩm" trong phần Thiết lập Người dùng và cấp cho nhóm đó quyền truy cập đến trường Giá vốn trên form & danh sách Sản phẩm.
* Nói cách khác, chỉ có người dùng thuộc nhóm "Truy Cập Giá Tiêu Chuẩn Sản Phẩm" mới có thể nhìn thấy trường thông tin này.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'security/product_standard_price_security.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
