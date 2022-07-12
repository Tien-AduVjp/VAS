# -*- coding: utf-8 -*-
{
    'name': "OKR & Project Integrator",
    'name_vi_VN': "Tích hợp OKR với Dự án",

    'summary': """
Assign a task to an OKR Key Result or create tasks from an OKR Key Result""",

    'summary_vi_VN': """
Gắn các nhiệm vụ vào Kết quả then chốt trong OKR
    	""",

    'description': """

What it does
============
- This module bridges OKR application and Project application, thereby allowing users to create Projects and tasks associated with OKR.
- With this module, users can record the data and log timesheets for each individual task in OKR. Users can also split a project into smaller tasks to assign to different members of the project group.
- View in the OKR app when installed

Key Features
============
- Assign an OKR to a Project/Task
- Create a Project/Task in an OKR
- Track how many Goals & Key Results is assigned to a Project
- Track how many Projects/Tasks are included in one Objective & Key Results

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
- Mô-đun này cho phép người dùng liên kết ứng dụng OKR với ứng dụng Dự án, qua đó cho phép tạo Dự án và nhiệm vụ gắn với OKR.
- Với mô-đun này, người dùng có thể theo dõi tiến độ của mục tiêu cần hoàn thành, ghi nhận chấm công trên các task được gắn với OKR. Chức năng chia nhỏ dự án thành nhiều nhiệm vụ khác nhau cho phép người dùng phân tích nhiệm vụ và quản lý đội ngũ thực hiện, giai đoạn của dự án.
- Nằm trong ứng dụng OKR sau khi hoàn tất cài đặt

Tính năng nổi bật
=================
- Gán Mục tiêu & Kết quả then chốt vào một Dự án/ Nhiệm vụ bất kỳ
- Tạo một Dự án/ Nhiệm vụ ở trong một OKR
- Theo dõi một Dự án được gán với bao nhiêu Mục tiêu & Kết quả then chốt
- Theo dõi một Mục tiêu & Kết quả then chốt bao gồm bao nhiêu Dự án/ Nhiệm vụ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Human Resources/OKR',
    'version': '0.1',
    'depends': ['to_okr', 'project'],
    'data': [
        'security/security.xml',
        'views/okr_node_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
