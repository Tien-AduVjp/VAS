{
    'name': "Git Project Management",
    'name_vi_VN': "Quản lý Dự án & Git",

    'summary': """
Integrate Git Management and Project Management""",
    'summary_vi_VN': """Tích hợp Quản lý Git và Quản lý Dự án""",

    'description': """

What it does
============
- This module is built to integrate Git Management with Project Management.

Key Features
============
- Specify a Git Repository for a Project
- Specify a Git Branch for a Task
- Specify a Git Branch for an Issue

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Mô-đun này giúp tích hợp ứng dụng Quản lý Git với Quản lý Dự án.

Tính năng nổi bật
=================
- Chỉ định một Git Repository cho một dự án
- Chỉ định một Git Branch cho một nhiệm vụ
- Chỉ định một Git Branch cho một vấn đề

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Operations/Project',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_git', 'project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/git_branch_views.xml',
        'views/git_repository_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
