# -*- coding: utf-8 -*-
{
    'name': "PoS Delivery",
    'name_vi_VN': "Giao hàng PoS",
    'summary': """Create delivery from PoS screen.
         """,
    'summary_vi_VN': """Tạo giao hàng từ màn hình Pos.
         """,

    'description': """
What it does
============

This module allows you to create delivery orders on Point of Sales (PoS) screen without exiting 

Key features
============
On PoS screen, during order validation, PoS users can enable delivery by choosing the following field:

* Delivery method and delivery date and time.
* Customer and delivery address.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====

Mô-đun này cho phép bạn tạo đơn giao hàng ngay từ màn hình Điểm bán lẻ (PoS) mà không cần phải thoát ra ngoài.

Tính năng nổi bật
=================
Trên màn hình Pos, trong quá trình xác thực đơn hàng, nhân viên PoS có thể tạo đơn giao hàng và chọn các thông tin sau:

* Phương thức giao hàng và ngày giờ giao hàng.
* Khách hàng và địa chỉ giao hàng.

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'delivery'],

    # always loaded
    'data': [
        'data/stock_config_data.xml',
        'views/assets.xml',
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
