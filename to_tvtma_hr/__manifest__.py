{
    'name': "HR Applicant in Employee form",
    'name_vi_VN': "Xem hồ sơ ứng viên trên hồ sơ nhân viên",

    'summary': """
Allow users to view the related applicants at employee and partner form""",
    'summary_vi_VN': """
Cho phép xem các hồ sơ ứng viên liên quan từ form nhân viên và đối tác""",

    'description': """
Key Features
============
1. Add a applicants counter in employee form to allow users can view related applicants
2. Add a applicants counter in partner form to allow users can view related applicants
3. Add VAT field in employee form that is related to the corresponding partner record specified in the field Private Address

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
3. Thêm trường VAT trên hồ sơ nhân viên, được lấy từ địa chỉ riêng tư của đối tác tương ứng

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_job_view.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True, #TODO: Merge with module viin_hr in odoo 14
    'application': False,
    'auto_install': True,
    'price': 180.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
