{
    'name': "Enterprise Marks - Inventory",
    'name_vi_VN': 'Kích Hoạt Chức Năng Kho Vận',
    'summary': """
Replace Enterprise labels in Inventory Settings""",

    'summary_vi_VN': """
Thay thế các nhãn của Enterprise ở Thiết lập ứng dụng Kho vận
    	""",

    'description': """
What it does
============
* This module replace Enterprise labels in Inventory Settings
* This module will be auto installed

Editions Supported
==================
1. Community Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Module thay thế các nhãn ấn bản Enterprise trong Thiết lập ứng dụng Kho vận
* Module được cài đặt tự động

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
