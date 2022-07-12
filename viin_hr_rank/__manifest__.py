# -*- coding: utf-8 -*-
{
    'name': "HR Employee Rank",
    'name_vi_VN': "Chức danh Nhân viên",

    'summary': """
Manage your employee's rank which is defined as a combination of employee grade and role""",

    'summary_vi_VN': """
Quản lý chức danh của nhân viên bằng việc kết hợp vai trò và cập bậc của nhân viên""",

    'description': """
What it does
============
In additional to the job position (brought by the module Employee) and grade (brought by the module Employee Grade)
and role (brought by the module Employee Role), this module provides Employee Ranks.

A rank is defined by combining grade and role of an employee. For example, we have Product Developer as a role,
Junior and Senior are grades. By combining those, we will have 2 ranks:

* Junior Product Developer
* Senior Product Developer

On the employee form, HR officer can specify role and grade for an employee, then the software will automatically
assign a corresponding rank (if any) to the employee.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Bên cạnh chức vụ (cung cấp bởi module Nhân viên), cấp bậc (cung cấp bởi module Cấp bậc Nhân viên), vai trò (cung cấp
bởi module Vai trò Nhân viên) thì module này cung cấp thêm khái niệm Chức danh Nhân viên.

Chức danh được xác định bằng việc kết hợp vai trò và cấp bậc của nhân viên. Giả sử ta có vai trò Chuyên viên Phát triển
Sản phẩm và các cấp bậc Cấp cao, Cấp trung. Bằng việc kết hợp vai trò và cấp bậc, ta sẽ có thể tạo ra các chức danh:

* Chuyên viên Phát triển Sản phẩm Cấp cao
* Chuyên viên Phát triển Sản phẩm Cấp trung

Trên giao diện form của nhân viên, cán bộ nhân sự có thể thiết lập vai trò và cấp bậc cho nhân viên, phần mềm sẽ tự động
xác định chức danh tương ứng (nếu có) và gán cho nhân viên.

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
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_employee_grade', 'viin_hr_role', 'viin_hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_role_views.xml',
        'views/hr_rank_views.xml',
        'views/hr_department_views.xml',
        'views/hr_job_view.xml',
        'views/hr_employee_public_views.xml',
        'views/hr_employee_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'data/demo.xml',
    ],
    'images': [
    	 'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': ['to_hr_employee_grade', 'viin_hr_role'],
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
