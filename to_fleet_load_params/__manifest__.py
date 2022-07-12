# -*- coding: utf-8 -*-
{
    'name': 'Fleet Load Params',
    'name_vi_VN': 'Thông Số Tải Trọng Của Phương Tiện',
    'category': 'Human Resources',
    'summary': """
This module adds some fields/parameters to vehicles in your fleet""",
    'summary_vi_VN': """
Module này thêm một số trường/thông số cho phương tiện trong đội phương tiện của bạn""",
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'version': '1.0.0',
    'description': """
What it does
============
This module adds some fields/parameters to vehicles in your fleet for safe transportation purpose:

* Warning Volume
* Max Volume
* Warning Weight
* Max Weight

NOTE
----
This module is very basic with additional fields for vehicles. It aims to be a dependency for others to extend

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Module này thêm một số trường/thông số cho phương tiện trong đội phương tiện của bạn với mục đích vận chuyển an toàn:

* Dung tích Cảnh báo
* Dung tích Tối đa
* Tải trọng Cảnh báo
* Tải trọng Tối đa

Chú ý
-----
Module này rất cơ bản với các trường bổ sung cho phương tiện. Nó sẽ là module phụ thuộc để module khác mở rộng.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'depends': ['fleet'],
    'data': [
        'views/fleet_vehicle_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
