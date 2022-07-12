# -*- coding: utf-8 -*-
{
    'name': "HR Shift Rotation",
    'name_vi_VN': "Luân chuyển ca",
    'summary': """Managing weekly work schedule, working rules of employees.
        """,
    'summary_vi_VN': """Quản lý ca làm việc hàng tuần, các quy tắc, tiêu chuẩn làm việc của nhân viên.
        """,
    'description': """
What it does
============
Managing weekly work schedule, shift work rules of employees:

    * Allow to create, edit weekly work schedule for employees.
    * Allow quick creation of work schedules for multiple employees.
    * Manage rules, working time, leaves.
    * Attaching this module needs to integrate with related modules in odoo.

Editions Supported
==================
1. Community Edition.
2. Enterprise Edition.

    """,
    'description_vi_VN': """
Module này làm gì
=================
Quản lý ca làm việc hàng tuần, các quy tắc luân chuyển ca làm việc của nhân viên:

    * Cho phép tạo, chỉnh sửa ca làm việc hàng tuần cho nhân viên.
    * Cho phép tạo nhanh các ca làm việc cho nhiều nhân viên.
    * Quản lý các quy định, thời gian làm việc, xin nghỉ.
    * Việc cài đặt module này cần tích hợp với các module liên quan trong odoo.

Phiên bản được hỗ trợ
=====================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_advanced', 'to_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/scheduler_data.xml',
        'views/hr_contract.xml',
        'views/shift_rotation_rule_view.xml',
        'views/shift_scheduling_line_view.xml',
        'views/menu.xml',
        'wizard/shift_schedule_wizard.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
