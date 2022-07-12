# -*- coding: utf-8 -*-
{
    'name': "Git Management",
    'name_vi_VN': "Git",

    'summary': """Integrate Git and Odoo""",
    'summary_vi_VN': """Tích hợp Git và Odoo""",

    'description': """

What it does
============
* Git is a distributed code version control system that uses Git Repositories to store the change history. Each Repository comprises Branches - which represent specific versions of that repository from the main project. Developers can test changes on these Branches without interfering other developers' code.
* By default, developers will have to manually update changes in Git into their Odoo software, which is a waste of time and resources. This module is built to integrate Git and Odoo. 

Key Features
============
* Scan a Git Repository for list of branches
* Create corresponding branches in odoo

Note
====
* This module requires gitpython library which could be installed by firing the command 'pip install gitpython'
* Known Issues: Remote Git repository authentication is not supported yet. In the case of private repository, please use SSH protocol (e.g. ssh://git@github.com:username/reponame.git, etc)

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Mô tả
=====
- Git là một hệ thống quản lý phiên bản phân tán, hoạt động thông qua các kho lưu trữ (Git Repository) chứa toàn bộ lịch sử thay đổi. Mỗi Repository sẽ bao gồm các Branch (nhánh) đại diện cho các phiên bản cụ thể của Repository đó được tách ra từ project chính. Tại các Branch này, lập trình viên có thể thử nghiệm các thay đổi mà không bị xung đột code với các lập trình viên khác. 
- Theo mặc định, lập trình viên sẽ phải tự cập nhật các thay đổi trên Git vào phần mềm Odoo. Việc này tốn nhiều thời gian và công sức. Mô-đun này được xây dựng giúp tự động quét và tích hợp Git với Odoo. 

Tính năng nổi bật
=================
- Quét Git Repository để tìm danh sách các branch
- Tạo các branch tương ứng trong Odoo 

Thông tin thêm
==============
- Mô-đun này cần phải có thư viện gitpython. Thư viện này có thể được cài đặt bằng cách kích hoạt lệnh 'pip install gitpython'
- Vấn đề hiện tại: Chưa hỗ trợ xác thực kho lưu trữ Git từ xa. Đối với các kho lưu trữ riêng tư, vui lòng sử dụng giao thức SSH (ví dụ: ssh://git@github.com:username/reponame.git, v.v)

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Version Controls/Git',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'to_sshkey', 'to_base'],
    'external_dependencies' : {
        'python' : ['GitPython'],
    },
    # always loaded
    'data': [
        'data/module_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/git_repository_views.xml',
        'views/git_branch_views.xml',
        'wizard/authenticate_views.xml',
        'wizard/checkout_commit_views.xml',
        'wizard/wizard_git_url_add_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 198.9,
    'subscription_price': 9.93,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook'
}
