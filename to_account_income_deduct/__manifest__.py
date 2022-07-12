{
    'name': "Income Deduction Account Type",
    'name_vi_VN': "Kiểu Tài khoản Giảm trừ doanh thu",

    'summary': """
Add income deduction account type for better categorization""",
 'summary_vi_VN': """
Bổ sung kiểu tài khoản Giảm trừ Doanh thu""",

    'description': """
* New Account Type:

  * Name: Income Deduction
  * xml_id: to_account_income_deduct.data_account_type_revenue_deduct

    """,
    'description_vi_VN': """
* Kiểu tài khoản mới:

  * Tên: Giảm trừ doanh thu
  * xml_id: to_account_income_deduct.data_account_type_revenue_deduct

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

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
