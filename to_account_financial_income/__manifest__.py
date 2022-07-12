# -*- coding: utf-8 -*-
{
    'name': "Financial Income Account Type",
    'name_vi_VN': "Kiểu tài khoản Doanh thu Tài chính",

    'summary': """
Add Financial Income Account Type""",
'summary_vi_VN': """
Tạo thêm kiểu tài khoản Doanh thu Tài chính""",

    'description': """
* New Account Type

  * Name: Financial Income
  * xml_id: to_account_financial_income.data_account_type_financial_income

    """,
    'description_vi_VN': """
* Kiểu tài khoản mới

  * Tên: Doanh thu Tài chính
  * xml_id: to_account_financial_income.data_account_type_financial_income

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'data/data_account_type.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
