{
    'name': "Loan Management - Vietnam Accounting",
    'name_vi_VN': "Quản Lý Khoản Vay - Kế Toán Việt Nam",

    'summary': """
Default Loan Order Template receivable & payable accounts for Vietnam""",
    'summary_vi_VN': """
Điền tài khoản phải thu, phải trả mặc định cho mẫu hợp đồng vay/cho vay theo chuẩn mực kế toán Việt Nam""",

    'description': """
Key Features
============
Default Loan Order Template receivable & payable accounts for Vietnam

* Loan Borrowing Contracts: account ```3411 Borrowing loans```
* Loan Lending Contracts: account ```1283 Lending Loans```

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN':"""
Tính năng nổi bật
=================
Điền tài khoản phải thu, phải trả mặc định cho Hợp đồng Vay/Cho vay theo chuẩn mực kế toán Việt Nam

* Hợp đồng Vay: tài khoản ```3411 Các khoản đi vay```
* Hợp đồng Cho vay: tài khoản ```1283 Cho vay```

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_loan_management', 'l10n_vn_c200'],

    # always loaded
    'data': [
        'data/l10n_vn_chart_data.xml',
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
