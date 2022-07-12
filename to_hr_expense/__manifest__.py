{
    'name': "Expense Customization",
    'name_vi_VN': "Tùy chỉnh Chi Tiêu",

    'summary': """
Create invoice from hr expense""",

    'summary_vi_VN': """
Tạo hóa đơn từ chi tiêu
        """,

    'description': """
What it does
============
Allows you to customize some of the information when create expense

1. Allow to choose the vendor on the expense form
2. Allow to encode expense entries as vendor bills
3. Allow the user to choose taxes on expense declarations

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Cho phép bạn tùy chỉnh một số thông tin khi tạo chi tiêu

1. Cho phép chọn nhà cung cấp trên form chi tiêu
2. Cho phép ghi nhận các chi tiêu như là các hóa đơn nhà cung cấp
3. Cho phép người dùng có quyền chọn thuế

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Expenses',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense'],

    # always loaded
    'data': [
        'views/hr_expense_view.xml',
        'views/hr_expense_sheet_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
