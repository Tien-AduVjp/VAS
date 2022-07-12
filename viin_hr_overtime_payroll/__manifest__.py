# -*- coding: utf-8 -*-
{
    'name': "Overtime Payroll",
    'name_vi_VN': "Bảng Lương - Tăng ca",
    
    'old_technical_name': 'to_hr_overtime_payroll',

    'summary': """
Integrate Overtime Management and Payroll for overtime calculation in payroll""",

    'summary_vi_VN': """
Tích hợp ứng dụng Tăng ca và Bảng lương để tính toán tiền tăng ca ở ứng dụng Bảng lương
    """,

    'description': """
    
Key Features
============
This module is to integrate the Overtime and Payroll applications in order to automatically calculate the overtime wage in Payroll based on employee's contract wage, pay rate and overtime hours.

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
    
Tính năng nổi bật
=================
Mô-đun này tích hợp ứng dụng Tăng ca và Bảng lương để tự động tính lương làm thêm giờ trong Bảng lương dựa trên mức lương theo hợp đồng, tỷ lệ chi trả và số giờ làm thêm của nhân viên.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

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
    'version': '0.1.5',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_overtime', 'to_hr_payroll'],

    # always loaded
    'data': [
        'security/hr_payroll_security.xml',
        'report/hr_employee_overtime_views.xml',
        'views/hr_advantage_template_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/report_payslip_templates.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
