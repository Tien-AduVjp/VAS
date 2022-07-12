# -*- coding: utf-8 -*-
{
    'name': "Badge ID in Employee Name",
    'name_vi_VN': "Mã Nhân Viên Trong Tên Nhân Viên",
    'summary': """
Concatenate barcode and name""",
    'summary_vi_VN': """
Kết hợp mã Nhân viên với tên Nhân viên """,    
    'description': """
What it does
============
* "Badge ID in Employee Name" module was developed to assist businesses in managing employee attendance in the company, and at the same time, it helps to identify identity easily in case the company has many employees with the same name. For example, instead of searching by complicated employee name, typing some digits could be faster.
    
Key Features
============
* Allow searching for employee information by Badge ID.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Mô đun "Mã Nhân Viên Trong Tên Nhân Viên" được phát triển hỗ trợ doanh nghiệp trong việc quản lý điểm danh nhân sự trong công ty, đồng thời giúp xác định danh tính dễ dàng trong trường hợp công ty có nhiều nhân viên trùng tên với nhau. Ví dụ: Thay vì tìm kiếm theo tên nhân viên, việc nhập số có thể nhanh hơn.

Tính năng nổi bật
=================
* Cho phép tìm kiếm thông tin nhân viên theo mã nhân viên.

Ấn bản được hỗ trợ
==================
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
    'category': 'Human Resources',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
