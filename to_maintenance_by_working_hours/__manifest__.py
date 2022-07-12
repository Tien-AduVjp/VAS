# -*- coding: utf-8 -*-
{
    'name': "Maintenance By Working Hours",

    'summary': """Maitenance by working hours
        """,

    'summary_vi_VN': """Bảo trì thiết bị theo giờ máy chạy
        """,

    'description': """
What it does
============
* Allow user to declare average daily working hours and working hours between each preventive maintenance for equipments
* Compute automatic the next maintenance date

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Cho phép khai báo số giờ chạy trung bình hàng ngày của thiết bị, số giờ chạy của thiết bị giữa các giai đoạn bảo trì.
* Tự động tính toán ngày cần thực hiện bảo trì tiếp theo.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/maintenance_equipment_views.xml',

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
