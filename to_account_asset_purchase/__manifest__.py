{
    'name': "Assets Management - Purchase",
    'name_vi_VN': 'Tài sản - Mua hàng',

    'summary': """
Bridge between Assets Management and Purchase""",
    'summary_vi_VN': """
Mô-đun cầu nối giữa Tài sản và Mua hàng""",

    'description': """
What it does
============
* Bridge between Assets Management and Purchase
* Manage asset purchases and create asset records for depreciation calculations

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Mô-đun cầu nối giữa Tài sản và Mua hàng
* Quản lý việc mua các tài sản và tạo hồ sơ tài sản phục vụ cho việc tính toán khấu hao

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_account_asset', 'purchase'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
