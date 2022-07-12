# -*- coding: utf-8 -*-
{
    'name': "Overtime Attendance",
    'name_vi_VN': "",

    'summary': """
Integrate Overtime Management app with Attendance app for auto actual overtime recognition with attendance log """,

    'summary_vi_VN': """
Tích hợp ứng dụng quản lý tăng ca với Vào/Ra để tự động nhận diện giờ tăng ca thực tế
    	""",

    'description': """
    
Key Features
============
After this module is installed, the actual overtime work will be recognized by matching planned overtime registration with the actual attendance log.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
    
Tính năng nổi bật
=================
Sau khi mô-đun này được cài đặt, thời gian tăng ca thực tế sẽ được ghi nhận bằng cách khớp các đăng ký tăng ca được lên kế hoạch sẵn với dữ liệu vào ra.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Overtime',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_attendance', 'viin_hr_overtime'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/overtime_plan_line_attendance_match_views.xml',
        'views/hr_overtime_plan_line_views.xml',
        'views/hr_overtime_plan_views.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
