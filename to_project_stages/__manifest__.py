{
    'name': "Project Stages",
    'name_vi_VN':"Giai Đoạn Dự Án",

    'summary': "Configure project stages",
    'summary_vi_VN': "Cấu hình giai đoạn dự án",

    'description': """
Key Features
============
This module:

* Allows to change the projects form view for users to organise specific stages for projects
* Allows to set color for each of the stages and according to that, users can identify the exact stage of projects/tasks in Kanban View (If tasks have been grouped by a certain criterion)

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Mô-đun này:

* Cho phép người dùng thay đổi giao diện dự án để tổ chức các giai đoạn cụ thể cho dự án
* Cho phép thiết lập màu sắc cho từng giai đoạn và nhờ đó, người dùng có thể nhận biết được nhiệm vụ đang ở giai đoạn nào khi ở Kanban view (Trong trường hợp nhiệm vụ đã được nhóm theo 1 tiêu chí nào đó).

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'version' : '0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category' : 'Project',
    'sequence': 11,
    # any module necessary for this one to work correctly
    'depends': ['project'],
    # always loaded
    'data': [
        'views/project_stages_view.xml',
        'views/project_task_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
