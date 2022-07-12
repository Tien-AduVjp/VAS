# -*- coding: utf-8 -*-
{
    'name': "HR Timesheet Approval",
    'name_vi_VN': "Phê duyệt Bảng chấm công Nhân sự",

    'summary': """
Allow approval of employee's timesheets""",

    'summary_vi_VN': """
Cho phép phê duyệt bảng chấm công của nhân viên""",

    'description': """
What it does
============
Allow approval of employee's timesheets, restrict employees'inaccurate reports.

Key features
============
* Managers can configurate the HR Timesheet approval with 4 types of validation: No validation, Approval Officer, Manager, Manager and Approval Officer. 
* Employees create a request integrated with the timesheet.
* Managers can 'Approve' or 'Refuse' the request.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Cho phép phê duyệt bảng chấm công của nhân viên, hạn chế việc khai báo không chính xác của nhân viên

Tính năng nỏi bật
=================
* Người quản lý có thể thiết lập 4 kiểu phê duyệt: Không cần xác nhận, Cán bộ phê duyệt, Quản lý trực tiếp, Quản lý trực tiếp và Cán bộ phê duyệt.
* Nhân viên tạo một yêu cầu phê duyệt tích hợp với bảng chấm công. 
* Người quản lý có thể Duyệt hoặc Từ chối yêu cầu

Ấn bản được hỗ trợ
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
    'category': 'Operations/Timesheets',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_contract',
        'hr_timesheet',
        'to_approvals',
        'project_timesheet_holidays',  # this integration avoid loading Time-off timesheet data as this should not require approval
        'viin_remove_only_reference_from_one2many', # this to remove the one2many field association without removing it from the database
        ],

    # always loaded
    'data': [
        'views/hr_department_views.xml',
        'views/hr_job_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_timesheet_views.xml',
        'views/approval_request_views.xml',
        'wizard/timesheet_approval_request_create.xml',
    ],
     # only loaded in demonstration mode
    'demo': [
        'demo/res_users_demo.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['to_approvals', 'hr_timesheet'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
