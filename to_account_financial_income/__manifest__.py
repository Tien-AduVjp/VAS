{
    'name': "Financial Income Account Type",
    'name_vi_VN': "Kiểu tài khoản Doanh thu Tài chính",

    'summary': """
Add Financial Income Account Type""",
    'summary_vi_VN': """
Tạo thêm kiểu tài khoản Doanh thu Tài chính""",

    'description': """
Key Features
============
* New Account Type

  * Name: Financial Income
  * xml_id: to_account_financial_income.data_account_type_financial_income

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng
=========
* Kiểu tài khoản mới

  * Tên: Doanh thu Tài chính
  * xml_id: to_account_financial_income.data_account_type_financial_income

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting',
    'version': '0.1.0',
    'depends': ['account'],
    'data': [
        'data/account_account_type_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
