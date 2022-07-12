# -*- coding: utf-8 -*-
{
    'name': "Repair Request with Maintenance Schedule",
    'name_vi_VN': "Yêu Cầu Sửa Chữa Với Lịch Bảo Trì",
    'summary': """Add repair jobs and parts based on maintenance schedule data""",
    'summary_vi_VN': """Thêm phụ tùng và công việc sửa chữa dựa trên dữ liệu lịch bảo trì""",
    'description': """
What it does
============
When a equipment has been set Maintenance schedule (milestone, parts, actions, v.v), this module helps update that data on Repair order created from Mantainenance request
for that equipment.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Khi một thiết bị được thiết lập Lịch bảo trì định kỳ (mốc thời gian bảo trì, phụ tùng cần bảo trì, công việc cần làm, v.v), mô-đun này giúp cập nhật các dữ liệu đó
lên Lệnh sửa chữa được tạo từ Yêu cầu bảo trì cho thiết bị đó.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_repair_request_from_maintenance', 'to_maintenance_notification'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
