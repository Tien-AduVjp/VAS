{
    'name': "Employee Resignations Management [Experimental]",
    'name_vi_VN': "Quản lý nhân viên thôi việc",

    'summary': """
Manage employee resignations and resignation tasks""",

    'summary_vi_VN': """
Quản lý đơn thôi việc và các nhiệm vụ khi nhân viên thôi việc
        """,

    'description': """
What it does
============
Manage employee resignations and resignation tasks.

Key Features
============
* Allow create resignations, approve resignations.
* When the resignation is approved, automatically launch Plan that is selected on the resignations.


Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Quản lý đơn thôi việc và các nhiệm vụ khi nhân viên thôi việc.

Tính năng chính
===============
* Cho phép tạo đơn thôi việc, phê duyệt đơn thôi việc
* Khi đơn xin thôi việc được phê duyệt, tự động khởi động Kế hoạch đã được chọn trên đơn xin thôi việc này.


Ấn bản được Hỗ trợ
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
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/hr_employee_resignation_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_plan_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
