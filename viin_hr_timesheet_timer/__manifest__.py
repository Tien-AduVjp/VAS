# -*- coding: utf-8 -*-
{
    'name': "HR Timesheet Timer",
    'name_vi_VN': "Bộ đếm thời gian chấm công",

    'summary': """Provide start/stop button on tasks to ease timesheet entry log""",

    'summary_vi_VN': """
Cung cấp nút Khởi động/Dừng trên nhiệm vụ để đơn giản hóa chấm công
""",

    'description': """
Key Features
============
* Start logging timesheet on a project task when you start/resume the task by hitting `Log Timesheet` button on the form view of the task.
* Stop logging timesheet on a project task when you pause/finish the task by hitting `Stop Timesheet Log` button on the form view of the task.
* New filter to find all the tasks that having your own work-in-progress timesheet entry
* New filter to Find all the tasks that having a work-in-progress timesheet entry by anyone

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Khởi động việc chấm công bằng nút Bắt đầu chấm công ở trên giao diện form của nhiệm vụ
* Dừng việc chấm công bằng nút Dừng chấm công ở trên giao diện form của nhiệm vụ
* Bộ lọc mới để tìm ra các nhiệm vụ mình mà đang chấm công dở dang
* Bộ lọc mới để tìm ra các nhiệm vụ mà có ai đó đang chấm công dở dang

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Timesheets',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['to_base', 'hr_timesheet', 'viin_web_countup_timer'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_timesheet_views.xml',
        'views/project_task_views.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['hr_timesheet'],
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
