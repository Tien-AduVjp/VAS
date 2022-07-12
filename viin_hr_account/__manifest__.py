{
    'name': "HR Accounting",
    'name_vi_VN': "Kế toán Nhân sự",

    'summary': """
Base module for Human Resource Accounting""",

    'summary_vi_VN': """
Module cơ sở tích hợp kế toán và nhân sự
    	""",

    'description': """
What it does
============
* Normally, accountants will have to manually input and manage expenses related to HR departments in the journal. This module provides base for integration between HR and Accounting (incl. General and Analytic)

Key Features
============
1. Generate accounts for HR Departments

   * Analytic Account will be generated for each HR department upon department creation
   * Specified general account for each department

2. Manage Analytic Accounts

   * Links to an HR department
   * Synchronizes account name and department name

3. Create and Edit Analytic Tags

   * Links to multiple HR departments
   * Auto suggest cost/revenue distribution for departments

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Thông thường, kế toán sẽ phải nhập và quản lý thủ công các chi phí liên quan đến các phòng ban nhân sự vào sổ bút toán. Mô-đun này giúp cung cấp các tính năng cơ sở để tích hợp Kế toán với Nhân sự

Tính năng nổi bật
=================
1. Tạo tài khoản quản trị cho các Phòng ban

   * Tự động tạo tài khoản quản trị khi tạo phòng ban
   * Thiết lập tài khoản kế toán cho từng phòng ban

2. Quản lý các tài khoản quản trị

   * Liên kết tài khoản quản trị với một phòng ban
   * Đồng bộ tên tài khoản quản trị với tên phòng ban

3. Tạo và chỉnh sửa các thẻ quản trị

   * Liên kết đến các phòng ban
   * Tự động gợi ý phân bổ doanh thu / chi phí cho các phòng ban

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
    'category': 'Accounting/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'hr', 'viin_hr'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_analytic_account_views.xml',
        'views/account_analytic_tag_views.xml',
        'views/account_payment_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
    ],
    'images': [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['account', 'hr'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
