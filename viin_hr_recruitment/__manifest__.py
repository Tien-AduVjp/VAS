{
    'name': "Viin HR Recruitment",
    'name_vi_VN': "Viin HR Recruitment",
    'old_technical_name': 'to_tvtma_hr',
    'summary': """
Allow users to view the related applicants at employee and partner form""",
    'summary_vi_VN': """
Cho phép xem các hồ sơ ứng viên liên quan từ form nhân viên và đối tác""",

    'description': """
Key Features
============
1. Add a applicants counter in employee form to allow users can view related applicants
2. Add a applicants counter in partner form to allow users can view related applicants

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
1. Thêm bộ đếm ứng viên trên form nhân viên cho phép người dùng xem các hồ sơ ứng viên liên quan
2. Thêm bộ đếm ứng viên trên form đối tác cho phép người dùng xem các hồ sơ ứng viên liên quan

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources/Recruitment',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'viin_hr', 'hr_recruitment'],

    # always loaded
    'data': [
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['hr', 'hr_recruitment'],
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
