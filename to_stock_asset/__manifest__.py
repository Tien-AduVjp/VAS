{
    'name': "Stock Asset",
    'name_vi_VN': "Tài Sản Và Kho",

    'summary': """
Integrate Asset Management with Inventory application for asset allocation""",

    'summary_vi_VN': """
Tích hợp ứng dụng Quản Lý Tài sản với ứng dụng Kho để cấp phát tài sản""",

    'description': """
What it does
============
Integrate Asset Management with Inventory application for asset allocation

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tích hợp ứng dụng Quản Lý Tài sản với ứng dụng Kho để cấp phát tài sản

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
    # Check https://github.com/tvtma/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1.3',

    # any module necessary for this one to work correctly
    'depends': ['to_account_asset', 'stock_landed_costs', 'to_stock_account_moves_link'],

    # always loaded
    'data': [
        'data/to_stock_asset_data.xml',
        'wizard/asset_stock_in_wizard.xml',
        'views/account_asset_asset_views.xml',
        'views/account_asset_category_views.xml',
        'views/stock_move_line_views.xml',
        'views/stock_move_views.xml',
        'views/stock_picking_type_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_production_lot_views.xml',
        'reports/account_asset_report_views.xml',
        'wizard/account_asset_asset_add_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
