{
    'name': "Project Kanban State Notification",
    'name_vi_VN': "Thông báo trạng thái kanban của dự án",

    'summary': """Project manager will be notified of any changes to kanban states of project tasks.""",

    'summary_vi_VN': """Người quản lý dự án sẽ được thông báo về bất cứ thay đổi nào tới trạng thái kanban của những nhiệm vụ dự án.""",

    'description': """
What it does
============

This module allows project manager to be notified of any changes to kanban states of project tasks.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Module này làm gì
=================

Mô-đun này cho phép người quản lý dự án nhận được thông báo về bất cứ thay đổi nào tới trạng thái kanban của các nhiệm vụ dự án.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Operations/Project',
    'version': '0.1.1',
    'depends': ['project'],
    'data': [
        'data/project_data.xml',
        'views/project_views.xml'
        ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
