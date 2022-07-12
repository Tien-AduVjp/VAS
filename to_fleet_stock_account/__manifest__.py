# -*- coding: utf-8 -*-
{
    'name': "Fleet Stock Consumption Accounting",
    'name_vi_VN': 'Kế Toán Xuất Kho Tiêu Thụ Cho Đội Phương Tiện',
    'summary': """
Integrates fleet stock and fleet accounting and""",
    'summary_vi_VN': """
Tích hợp kho cho đội phương tiện và kế toán cho đội phương tiện""",
    'description': """
What it does
============
This application integrates the following applications to offer links between stock moves, fleet vehicles, fleet costs and journal items for keeping track on such information

* Fleet Stock Consumption
* Fleet Accounting
* Stock Accounting (the one in the standard Odoo delivery)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Ứng dụng này tích hợp các ứng dụng sau để cung cấp các liên kết giữa di chuyển kho, đội phương tiện, chi phí đội phương tiện và các mục nhật ký để theo dõi thông tin đó

* Xuất Kho Tiêu Thụ Cho Đội Phương Tiện
* Kế Toán Đội Phương Tiện
* Kế Toán Kho (là một trong giao hàng Odoo tiêu chuẩn)

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_stock', 'to_fleet_accounting'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
