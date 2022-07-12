{
    'name': "Project Access Rights - Timesheets",
    'name_vi_VN': "Quyền truy cập dự án - Chấm công",
    'summary': """Access control for project timesheets""",
    'summary_vi_VN': """Kiểm soát quyền truy cập chấm công của dự án""",
    'description': """
What it does
============
This module provides the permissions to view all timesheets in projects.

Key Features
============
If the project is marked as "Grant Full Access Rights". The project manager can view all timesheets in this project.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này bổ sung thêm quyền xem tất cả các chấm công trong dự án.

Tính năng nổi bật
=================
Nếu dự án được đánh dấu là "Cấp toàn quyền truy cập", chủ nhiệm dự án có thể xem tất các các chấm công của mọi người trong dự án này.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project/Timesheets',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_timesheet', 'to_project_access'],

    # always loaded
    'data': [
        'security/module_security.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'images' : [],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
