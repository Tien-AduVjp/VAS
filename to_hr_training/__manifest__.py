# -*- coding: utf-8 -*-
{
    'name': "HR Employee Training",
    'name_vi_VN': "Đào Tạo Nhân Viên",

    'summary': """
Manage courses for each position, each rank
""",

    'summary_vi_VN': """
Quản lý các khóa học cho từng chức vụ, từng chức danh
    	""",

    'description': """

Key Features
============

- Choose the courses per employee's position and rank when HR installs information on the *Employee* app
- Automatically calculate the corresponding courses for current rank and courses for next targeted rank when HR installs information in the *Employee* app
- Courses for the current rank consist of courses for the employee's current rank and courses for all of the lower ranks
- Courses for the next goal rank consist courses for the higher rank next to the existing rank of the employee

Supported Editions
==================

1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Tính năng nổi bật
=================

- Chọn các khóa học cho từng chức vụ và chức danh khi Nhân sự cài đặt thông tin trên ứng dụng *Nhân viên*
- Tự động tính toán các khóa học tương ứng cho chức danh hiện hành và chức danh mục tiêu kế tiếp khi Bộ phận Nhân sự cài đặt thông tin trên ứng dụng *Nhân viên*
- Các khóa học cho chức danh hiện hành bao gồm các khóa học cho chức danh hiện hành của nhân viên và các khóa học của tất cả chức danh thấp hơn của nhân viên đó
- Các khóa học cho chức danh mục tiêu kế tiếp bao gồm các khóa học cho chức danh có cấp bậc cao hơn liền kề với chức danh hiện tại của nhân viên

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/Viindoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Training',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_skill_framework', 'website_slides'],

    # always loaded
    'data': [
        'views/hr_rank_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_skill_description_views.xml',
        'views/hr_job_views.xml',
        'views/slide_channel_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
