# -*- coding: utf-8 -*-
{
    'name': "Git Branch Odoo Version",
    'name_vi_VN': "Phiên bản Odoo Git Branch",

    'summary': """
Map Git Branches with Odoo Versions""",
   'summary_vi_VN': """Kết nối Git Branch với phiên bản Odoo tương ứng""",

    'description': """

What it does
============
- By default, developers will have to manually update and connect Git branches to the corresponding Odoo version, which takes a lot of time and effort.
- This module automatically maps an existing git branch with an existing Odoo version for identication purpose

Key Features
============
- Scan a Git Repository for list of branches
- Automatically map existing Git Branches with corresponding Odoo version

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Theo mặc định, lập trình viên sẽ phải tự cập nhật, kết nối các Git Branch vào phiên bản Odoo tương ứng. Việc này rất tốn thời gian và công sức.
- Mô-đun này được xây dựng giúp tự động kết nối một nhánh Git hiện có với phiên bản Odoo tương ứng cho mục đích nhận dạng

Tính năng nổi bật
=================
- Quét các Git Branch trên Git Repository
- Tự động kết nối các Git Branch với phiên bản Odoo tương ứng

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
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Operations/Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_git', 'to_odoo_version', 'to_product_license'],

    # always loaded
    'data': [
        'views/git_branch_views.xml',
        'views/git_repository_views.xml',
        'views/odoo_version_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
