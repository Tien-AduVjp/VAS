# -*- coding: utf-8 -*-
{
    'name': "Payroll Timesheet Integrator",
    'name_vi_VN': "Tích hợp Chấm công với Bảng lương",

    'summary': """
Integrate employee timesheet with TVTMA HR Payroll""",

    'summary_vi_VN': """
Tích hợp Chấm công với ứng dụng Bảng lương TVTMA
    	""",

    'description': """
What it does
============
This application integrates HR Timesheet application and TVTMA HR Payroll application to allow payroll user to consider timesheets in HR payslips

Key Features
============
1. Collect employee timesheet log and store in payslip for payroll calculation

   * Timesheet collected will be according to the payslip's period

2. Automatic update employee's Timesheet Cost everyday based on its latest payslip's company cost.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition (without installation of the its Payroll app. The module requires TVTMA Payroll, not the EE Payroll)

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này tích hợp ứng dụng chấm công và ứng dụng bảng lương TVTMA để cho phép người tính lương xem xét chấm công trên bảng lương

Tính năng chính
===============
1. Thu thập các dòng chấm công và lưu trữ trong bảng lương để tính toán.

   * Bảng chấm công thu thập được sẽ dựa vào khoảng thời gian của bảng lương

2. Tự động cập nhật chi phí chấm công của nhân viên mỗi ngày dựa vào chi phí công ty trên bảng lương mới nhất của họ.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise (không cần cài đặt ứng dụng Payroll của nó. Mô-đun yêu cầu Bảng lương TVTMA, không phải Bảng lương EE)

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet', 'to_hr_payroll'],

    # always loaded
    'data': [
        'data/hr_payroll_data.xml',
        'security/module_security.xml',
        'wizard/timesheet_cost_update.xml',
        'views/hr_payroll_structure_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_job_views.xml',
        'views/hr_contract_views.xml',
    ],

    'images' : [
    	# 'static/description/main_screenshot.png'
    	],
    
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
