{
    'name': "Stock Asset Equipment",
    'name_vi_VN': "Tài Sản Thiết bị Và Kho",

    'summary': """
Integrate Asset Management with Stock Equipment application for management equipment as asset""",

    'summary_vi_VN': """
Tích hợp ứng dụng Quản Lý Tài sản với ứng dụng Thiết Bị Và Kho để quản lý tài sản thiết bị""",

    'description': """
What it does
============
Integrate Asset Management with Stock Equipment application for management equipment as asset

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Tích hợp ứng dụng Quản Lý Tài sản với ứng dụng Thiết Bị Và Kho để quản lý tài sản thiết bị

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
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_asset', 'to_stock_equipment'],

    # always loaded
    'data': [
        'views/account_asset_asset_views.xml',
        'views/stock_production_lot_views.xml',
        'views/maintenance_equipment_views.xml',
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
    'installable': True,
    'application': False,
    'auto_install': False, # set True after upgrade to 13
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
