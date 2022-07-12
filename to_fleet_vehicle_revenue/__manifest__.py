# -*- coding: utf-8 -*-
{
    'name': "Fleet Vehicle Revenue Modeling",
    'name_vi_VN': 'Mô Hình Hóa Doanh Thu Của Đội Phương Tiện',
    'summary': """
Fleet Vehicle Revenue Modeling module provides of the model Fleet Vehicle Revenue
""",
    'summary_vi_VN': """
Mô-đun Mô Hình Hóa Doanh Thu Của Đội Phương Tiện cung cấp model của Doanh Thu Đội Phương Tiện
""",
    'description': """
Key Features
============
This module provides start point for further development of features concerning to fleet vehicle revenue. Except the provision of the model Fleet Vehicle Revenue (fleet.vehicle.revenue), it does nothing.

1. The fields of the Vehicle Revenue model:

    * Vehicle: The name of the vehicle related to the current revenue record
    * Revenue Subtype: to categories vehicle revenue
    * Amount: the revenue amount
    * Odometer: refering to an odometer record at the time of revenue raising
    * Date: the date of revenue
    * Auto Generated: a technical field to indicated if the revenue record is generated automatically by another instead of being recorded manually by human

2. Auto-Generate Odometer record during Revenue creation

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
Mô-đun này cung cấp điểm khởi đầu để phát triển hơn nữa các tính năng liên quan đến doanh thu của đội phương tiện. Ngoại trừ việc cung cấp Mô Hình Doanh Thu Của Đội Phương Tiện (fleet.vehicle.revenue), nó không làm gì cả.

1. Các trường của mô hình Vehicle Revenue:

     * Vehicle: tên của xe liên quan đến bản ghi doanh thu hiện tại
     * Revenue Subtype: để phân loại doanh thu của xe
     * Amount: số tiền doanh thu
     * Odometer: tham chiếu đến một bản ghi của công tơ mét tại thời điểm tăng doanh thu
     * Date: Ngày doanh thu
     * Auto Generated: trường kỹ thuật để chỉ định nếu bản ghi doanh thu được tạo tự động bởi người khác thay vì được ghi bằng tay bởi con người

2. Tự động tạo bản ghi của công tơ mét trong quá trình tạo doanh thu

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

""",

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_revenue_view.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
