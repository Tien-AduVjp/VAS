# -*- coding: utf-8 -*-
{
    'name': "Overtime Timesheet",
    'name_vi_VN': "Chấm công Tăng ca",

    'summary': """
Integrate Timesheet and Overtime for automatic overtime work recognition using timesheet""",

    'summary_vi_VN': """
Tích hợp Chấm công và Tăng ca để tự động nhận diện làm việc ngoài giờ sử dụng chấm công""",

    'description': """
What it does
============
This module integrates Timesheet app and Overtime app for automatic overtime work recognition using timesheet

Key Features
============
1. Define overtime plans for employee
2. Log timesheet using Timesheet app
3. Overtime recognition will be done automatically by matching the plans and the actual timesheet log

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này tích hợp ứng dụng Chấm công và ứng dụng Tăng ca để tự động nhận diện làm việc ngoài giờ sử dụng dữ liệu chấm công

Tính năng chính
===============
1. Thiết lập kế hoạch tăng ca
2. Ghi thời gian làm việc thực tế sử dụng ứng dụng chấm công
3. Tự động nhận diện thời gian làm việc thực tế khớp với kế hoạch tăng ca

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
    'depends': [
        'viin_hr_overtime',
        'viin_hr_timesheet_timer',
        'project_timesheet_holidays',  # this integration avoid loading Time-off timesheet data as this should not require approval
        ],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/overtime_plan_line_timesheet_match_views.xml',
        'views/hr_overtime_plan_line_views.xml',
        'views/hr_overtime_plan_views.xml',
        'views/hr_overtime_reason_views.xml',
        'wizard/hr_overtime_request_mass_views.xml',
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
