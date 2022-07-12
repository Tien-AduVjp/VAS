{
    'name': "Income Deduction Account Type",
    'name_vi_VN': "Kiểu Tài khoản Giảm trừ doanh thu",

    'summary': """
Add income deduction account type for better categorization""",
    'summary_vi_VN': """
Bổ sung kiểu tài khoản Giảm trừ Doanh thu""",

    'description': """
Key Features
============
* New Account Type:

  * Name: Income Deduction
  * xml_id: to_account_income_deduct.data_account_type_revenue_deduct

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng
=========
* Kiểu tài khoản mới:

  * Tên: Giảm trừ doanh thu
  * xml_id: to_account_income_deduct.data_account_type_revenue_deduct

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
