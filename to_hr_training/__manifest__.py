# -*- coding: utf-8 -*-
{
    'name': "HR Employee Training",
    'name_vi_VN': "Đào Tạo Nhân Viên",

    'summary': """
Manage required courses for each job position, each grade
""",

    'summary_vi_VN': """
Quản lý các khóa học yêu cầu cho từng vị trí công việc, từng cấp bậc.
    	""",

    'description': """

Key Features
============

- Choose the required courses & minimum study time per employee's position and rank when HR installs information on the *Employee* app
- Automatically calculate the corresponding required courses when HR installs information in the *Employee* app
- Required courses of each employee will correspond to their position/ grade and all subordinates of that employee grade

Supported Editions
==================

1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Tính năng nổi bật
=================

- Chọn các khóa học bắt buộc và thời gian học tối thiểu tương ứng cho từng vị trí công việc và thứ bậc khi Nhân sự cài đặt thông tin trên ứng dụng *Nhân viên*
- Tự động tính toán các khóa học bắt buộc tương ứng cho từng vị trí công việc và thứ bậc khi Bộ phận Nhân sự cài đặt thông tin trên ứng dụng *Nhân viên*
- Các khóa học yêu cầu sẽ tương ứng với vị trí công việc/ thứ bậc của nhân viên và tất cả cấp dưới của nhân viên đó.

Ấn bản được Hỗ trợ
==================

1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Training',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_hr_employee_grade', 'website_slides'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_grade_views.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_views.xml',
        'report/employee_training_report_view.xml',
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
