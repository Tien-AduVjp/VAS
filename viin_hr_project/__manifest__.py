{
    'name': "Project & HR Integration",
    'name_vi_VN': "Tích hợp Dự án & Nhân sự",

    'summary': """
Integrate the HR module into the Project module
""",

    'summary_vi_VN': """
Tích hợp ứng dụng dự án với nhân sự
    	""",

    'description': """
What it does
============
1. Allow group by Department HR in Project model and Task model
2. Reporting timesheet by Department HR
3. Filter tasks by: My Department 's Tasks, My Department Involve Tasks, My Subordinate 's Tasks, My Subordinate Involve Tasks


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
1. Cho phép nhóm theo Department trên model Project và model Task
2. Báo cáo timesheet theo Department
3. Bộ lọc các tác vụ theo: Tác vụ của phòng ban người dùng, tác vụ liên quan đến phòng ban của người dùng, Tác vụ của nhân viên nhân viên dưới cấp, Tác vụ liên quan đến nhân viên dưới cấp.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Operations/Project',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['project','hr_timesheet','hr_org_chart'],

    # always loaded;,;
    'data': [      
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/account_analytic_line_views.xml',
    ],
    'pre_init_hook':'_pre_init_hook',
    # only loaded in demonstration mode
    'demo': [],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
