{
    'name': "Inventory Adjustment with Cost Price",
    'name_vi_VN': "Kiểm Kê Kho Với Giá Vốn",

    'summary': """
Inventory Adjustment with Cost Price""",

    'summary_vi_VN': """
Kiểm kê kho với giá vốn
    	""",

    'description': """
What it does
============
Inventory adjustment with cost price when counted quantity is more than the on hand quantity in stock

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Kiểm kê kho với giá vốn khi số lượng đã đếm nhiều hơn số lượng thực tế trong kho

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
    'category': 'Operations/Inventory',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/stock_inventory_line_views.xml',
        'views/stock_quant_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
