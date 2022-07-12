# -*- coding: utf-8 -*-
{
    'name': "HR Employee Grade",
    'name_vi_VN': "Cấp bậc Nhân viên",

    'summary': """
Managing Employee Grade. 
        """,

    'summary_vi_VN': """
Quản lý Cấp bậc Nhân viên.
    	""",

    'description': """
What it does
============
* In addition to the position, employees will be classified by grades, for example: Internship, Junior, Senior. This module helps manage each employee's grade.
* You can find this module in "Configuration" of the "Employee" App when installed. 

Key Features
============
* Allows users to create employee grade.
* Allows users to classify, filter and easily search for employee information by employee grade in Employee Directory.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Ngoài vị trí, nhân viên sẽ được phân loại theo từng cấp bậc, ví dụ: Intership, Junior, Senior. Mô đun này giúp quản lý cấp bậc của từng nhân viên.
* Người dùng có thể tìm mô đun "Quản lý cấp bậc nhân viên" này trong "Cấu hình" của ứng dụng "Nhân viên" sau khi hoàn tất cài đặt.

Tính năng nổi bật
=================
* Cho phép tạo Cấp bậc nhân viên.
* Cho phép phân loại, lọc và dễ dàng tìm kiếm thông tin nhân viên theo cấp bậc trong Danh bạ nhân viên.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/grade_data.xml',
        'views/hr_employee_grade_views.xml',
        'views/hr_employee_public_views.xml',
        'views/hr_employee_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
