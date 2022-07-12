# -*- coding: utf-8 -*-
{
    'name': "Overtime Timesheet Approval",
    'name_vi_VN': "Duyệt Chấm công cho Tăng ca",

    'summary': """Technical module to bridge Overtime Timesheet and Timesheet Approval modules""",

    'summary_vi_VN': """
Ứng dụng cầu nối cho module Chấm công Tăng ca và Phê duyệt chấm công
    	""",

    'description': """
Technical module to bridge Overtime Timesheet and Timesheet Approval modules to exclude unapproved timesheet from overtime recognition

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Module kỹ thuật làm cầu nối giữa module Chấm công tăng ca và Duyệt chấm công để loại trừ các chấm công không được duyệt ra khỏi giờ tăng ca

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
    'depends': ['viin_hr_overtime_timesheet', 'to_hr_timesheet_approval'],

    # always loaded
    'data': [
        'views/hr_overtime_plan_line_views.xml',
        'views/hr_overtime_plan_views.xml',
        'views/approval_request_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
