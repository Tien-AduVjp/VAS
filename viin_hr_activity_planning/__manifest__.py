{
    'name': "HR Activity Planning",
    'name_vi_VN': "Kế hoạch hoạt động nhân sự",

    'summary': """
Improve HR Activity Planning
    """,

    'summary_vi_VN': """
Nâng cấp mở rộng tính năng kế hoạch hoạt động của HR
    """,

    'description': """
What it does
============
Allow HR officer to launch plan for employees

Key Features
============
* Allow HR officer to launch plan for employee/manager/coach which is not from HR groups
* Manager/coach are able to see their employee's plans

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Cho phép nhân viên HR có thể lên các kế hoạch cho từng nhân viên/quản lý nhân viên/huấn luyện nhân viên

Tính năng chính
===============
* Cho phép nhân viên HR lên kế hoạch cho nhân viên/quản lý nhân viên/huấn luyện nhân viên mà nhân viên/quản lý nhân viên/huấn luyện nhân viên không cần phải thuộc nhóm cán bộ nhân sự
* Quản lý nhân viên/huấn luyện của nhân viên có thể xem các kế hoạch của nhân viên mà đang quản lý

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
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'views/hr_employee_public_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
