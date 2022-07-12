# -*- coding: utf-8 -*-
{
    'name': "HR Employee Role",
    'name_vi_VN': "Vai trò Nhân viên",

    'summary': """
Manage your employee's roles (e.g. Product Developer, Sales Executives, etc)""",

    'summary_vi_VN': """
Quản lý các vai trò nhân viên trong hệ thống nhân sự (vd: phát triển sản phẩm, chuyên viên kinh doanh, v.v.)""",

    'description': """
What it does
============
* In addition to the job position, employees could be classified by roles. For example: Product Developer, Sales Executives, etc.

Key Features
============
* HR Officer or Administrators can define an employee role that are dedicated for a department. For example: Product Developer
  is a role that dedicatedly belong to the Product Development department
* HR Officer or Administrators can define an employee role that are generic and available for any department.
* Each employee can be classified with a role

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Bên cạnh chức vụ, nhân viên cũng có thể được phân loại theo vai trò. Ví dụ: Chuyên viên Kinh doanh, Chuyên viên Phát triển Sản phẩm.

Tính năng chính
===============
* Cán bộ Nhân sự hoặc Quản trị viên có thể tạo các vai trò chuyên biệt cho phòng ban. Ví dụ: Chuyên viên Phát triển Sản phẩm là một vai trò
  chuyên biệt thuộc về bộ phận Phát triển sản phẩm.
* Cán bộ Nhân sự hoặc Quản trị viên có thể tạo các vai trò chung chung mà có thể áp dụng cho các phòng ban.
* Mỗi nhân viên có thể được gắn với một vai trò liên quan đến phòng mình hoặc một vai trò mà có thể áp dụng cho nhiều phòng ban

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
    'depends': ['hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_role_views.xml',
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
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
