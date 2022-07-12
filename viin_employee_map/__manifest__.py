{
    'name': "Employees Map",
    'name_vi_VN': "Bản đồ Nhân viên",

    'summary': """View employees in map view""",
    'summary_vi_VN': """Xem danh sách nhân viên trên giao diện bản đồ""",

    'description': """
What it does
============
This module add interactive map view for showing employees in map based on its private address and work address

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Cung cấp giao diện bản đồ để hiển thị địa chỉ cá nhân và địa chỉ làm việc của nhân viên.  

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'viin_web_map'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_public_views.xml',
        'views/hr_employee_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['hr'],
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
