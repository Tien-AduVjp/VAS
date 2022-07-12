{
    'name': "Vietnam - Meal Order Payroll with Accounting",
    'name_vi_VN': 'Việt Nam - Tích hợp lương bổng đặt suất ăn với Kế toán',

    'summary': """
Accounting Data for Vietnamese Meal Order Payroll Rules""",

    'summary_vi_VN': """
Dữ liệu kế toán Việt Nam cho quy định lương bổng đặt suất ăn
""",

    'description': """
Key Features
============
* Set Accounts for salary rules according to Vietnam Accounting Standard

    * HR Meal Order Deduction Amount:

        * Debit Account: 334
        * Credit Account: 1388

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
* Thiết lập tài khoản cho quy định lương theo chuẩn mực kế toán Việt Nam

    * HR Meal Order Deduction Amount:

        * Nợ: 334
        * Có: 1388

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
    'category': 'Localization',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_l10n_vn_hr_payroll_account', 'to_hr_payroll_meal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
