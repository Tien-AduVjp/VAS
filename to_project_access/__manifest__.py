# -*- coding: utf-8 -*-
{
    'name': "Project Access Rights",
    'name_vi_VN': "Quyền truy cập dự án",
    'summary': """Advanced Multi-level access control for projects and tasks""",
    'summary_vi_VN': """Kiểm soát quyền truy cập nâng cao cho dự án và nhiệm vụ""",
    'description': """
What it does
============
This module provides and modifies the permissions of Project module to improve the work management and collaboration

Key Features
------------
Modify the Project module permissions to the new set of permissions as follows:

* Internal User (aka Employee User): 

  * Can view the Project root menu entry 
  * Can view projects whose tasks are assigned to them
  * Cannot create/modify/delete tasks but can change the kanban state

* Project/User: 

  * Can do everything with the projects to which they are assigned as the project manager 
  * As for other projects and tasks, they will have the same access rights as the other internal users

* Project/Administrator: 

  * Can do everything in the Project application.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này bổ sung và chỉnh sửa phân quyền mô-đun Dự án để phù hợp hơn với việc quản lý công việc và làm việc cộng tác

Tính năng nổi bật
-----------------
Chỉnh sửa các quyền của mô-đun Dự án thành các bộ quyền mới như sau:

* Người dùng nội bộ (là Nhân viên):

  * Có thể thấy menu Dự án
  * Có thể thấy các dự án mà có chứa các task được giao cho mình
  * Không thể thêm, sửa, xóa, tạo các nhiệm vụ như có thể thay đổi trạng thái Kanban

* Dự án / Người dùng: 

  * Có toàn quyền với các dự án mà mình được phân công làm Chủ nhiệm dự án,
  * Đối với các dự án khác, có quyền giống với quyền của Người dùng nội bộ

* Dự án / Quản trị viên: 

  * Có toàn quyền ở ứng dụng Dự án

Ấn bản được hỗ trợ
==================
1. Ấn bản Community 
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Operations/Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project', 'to_base'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook'
}
