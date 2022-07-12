{
    'name': "Payroll By Administrative Regions",
    'name_vi_VN': "Bảng lương Theo Vùng Hành Chính",

    'summary': """Integrate the Payroll app and the Administrative Region app for applying administrative rules for salary and employee contribution calculation.""",
    'summary_vi_VN': """Tích hợp ứng dụng Bảng lương và ứng dụng Quản lý Vùng Hành chính để tính lương và các khoản đóng góp từ lương theo quy tắc vùng hành chính.""",

    'description': """
What it does
============
This module integrates the Payroll app and Administrative Region app to get payroll calculation to respect min/max wage and employee contributions according to administrative region rules.

Key Features
============
1. Minimum basic wage for employees in specific administrative regions
2. Mininum and maximum contributions (e.g. social insurance, unemployment insurance, etc) by employees and company according to  administrative regions specified

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Module này tích hợp ứng dụng Bảng lương và ứng dụng Quản lý Vùng Hành chính để giới hạn lương tối thiểu và các khoản đóng góp từ lương tối thiểu/tối đa theo quy tắc vùng hành chính.

Tính năng nổi bật
=================
1. Lương tối thiểu vùng
2. Đóng góp tối thiểu / tối đa theo vùng đối với các khoản đóng góp trích từ lương (vd: bảo hiểm xã hội, bảo hiểm thất nghiệp, v.v.)


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
    'category': 'Human Resources/Payroll',
    'version': '0.1.0',
    'depends': ['to_hr_payroll','viin_administrative_region'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/admin_region_payroll_contrib_views.xml',
        'views/administrative_region_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payroll_contribution_history_views.xml',
        'views/hr_payroll_contribution_register.xml',
        'views/res_country_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : [
         'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 198.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
