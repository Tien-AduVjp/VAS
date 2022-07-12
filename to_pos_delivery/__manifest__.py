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

Default, when delivery orders are created through Point of Sale (PoS), they are immediately marked as completed and considered delivered.
This module allows you to create delivery orders on Point of Sales (PoS) instead of completing the order.

Note: Delivery scheduling is only available for PoS that have Real-Time Inventory Management enabled.

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

Mặc định, khi đơn giao hàng được tạo thông qua Điểm bán lẻ (PoS) chúng sẽ được coi là đã giao và ngay lập tức được đánh dấu hoàn thành.
Mô-đun này cho phép bạn lên lịch cho đơn giao hàng từ màn hình Điểm bán lẻ (PoS) thay vì hoàn thành luôn đơn hàng.

Lưu ý: Tính năng lên lịch cho đơn chỉ hỗ trợ cho Điểm bán lẻ được thiết lập Quản lý kho theo thời gian thực.

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
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Point Of Sale',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'delivery', 'to_base'],

    # always loaded
    'data': [
        'data/stock_config_data.xml',
        'views/assets.xml',
        'views/pos_order_views.xml',
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
