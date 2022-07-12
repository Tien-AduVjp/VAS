{
    'name': "Stock Specific Identification",
    'name_vi_VN': "Giá vốn Thực tế Đích danh",

    'summary': """
Specific Identification Inventory Valuation method addition""",

    'summary_vi_VN': """
Bổ sung phương pháp định giá tồn kho theo Thực tế Đích danh
    	""",

    'description': """
What it does
============
Specific Identification Inventory Valuation method addition

Demo: https://youtu.be/mM7GNu-0gm0

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Bổ sung phương pháp định giá tồn kho Thực tế Đích danh

Demo: https://youtu.be/mM7GNu-0gm0

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_valuation_layer_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': [
    	'static/description/main_screenshot.png'
    	],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 299.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
