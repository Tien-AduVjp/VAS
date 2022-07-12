{
    'name': "Fleet Drivers Management",
    'name_vi_VN': "Quản Lý Lái Xe Của Đội Phương Tiện",
    'summary': """Manage drivers of your fleet""",
    'summary_vi_VN': "Quản lý lái xe của đội phương tiện của bạn",
    'description': """
What is does
============
This module, by integrating HR module and Fleet Management module and adding new features, allows you to manage all people (including your employees and subcontors' drivers) who serve your fleet as drivers

Key Features
------------
* Each driver associated with a partner and an employee (if the driver is an employee of the company's)
* Manage your drivers license and its expiration date
* Default data for driver lincense classes: A1, A2, B1, B2,...

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Module này làm gì
=================
Mô-đun này tích hợp mô-đun Nhân Sự và mô-đun Quản lý Đội Phương Tiện và thêm các tính năng mới, cho phép bạn quản lý tất cả mọi người (bao gồm cả nhân viên và tài xế) mà phục vụ đội phương tiện của bạn làm tài xế

Tính năng chính
---------------
* Mỗi tài xế liên kết với đối tác và nhân viên (nếu tài xế là nhân viên của công ty)
* Quản lý giấy phép lái xe của tài xế và ngày hết hạn
* Dữ liệu mặc định cho hạng giấy phép lái xe: A1, A2, B1, B2,...

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

    'category': 'Human Resources',
    'version': '2.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_partner_dob', 'hr_fleet'],

    # always loaded
    'data': [
        'data/driver_license_class_data.xml',
        'data/scheduler_data.xml',
        'security/ir.model.access.csv',
        'views/driver_views.xml',
        'views/hr_employee_views.xml',
        'views/class_views.xml',
        'views/driver_license_views.xml',
        'views/fleet_vehicle_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
