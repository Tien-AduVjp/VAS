{
    'name': "Foreign Trade & Landed Cost",
    'name_vi_VN': 'Ngoại Thương & Chi Phí Về Kho',
    'summary': """
Allocate importing costs as landed costs to the foreign imported goods 
        """,

    'summary_vi_VN': """
Phân bổ chi phí về kho cho lô hàng xuất nhập khẩu.
    	""",

    'description': """
What is does
============
1. This module extends the Foreign Trade application to integrate Landed Cost module to boost productivity.

2. When you validate a custom declaration that contains costs (e.g. importing taxes, etc), Odoo will automatically generate landed cost document for you to allocate the cost to the storable goods.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Module này làm gì
=================
1. Ứng dụng này tích hợp ứng dụng Xuất nhập khẩu và Phân bổ Chi phí về Kho (Landed Cost) để tăng cường hiệu suất, tự động hoá quy trình nhập khẩu hàng hoá và giảm thiểu lỗi gây ra bởi sự nhầm lẫn của con người khi phải thao tác với số liệu các lô hàng nhập khẩu.

2. Khi xác nhận phiếu khai báo hải quan cho lô hàng xuất nhập khẩu, nếu có các chi phí thuế phát sinh, hệ thống sẽ tự động tạo phân bổ chi phí về kho cho lô hàng này.

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
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_foreign_trade', 'stock_landed_costs'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/product_data.xml',      
        'views/stock_landed_cost_view.xml',
        'views/custom_declaration_import_views.xml',
        'views/custom_declaration_export_views.xml',
        'views/res_config_settings_views.xml'
        
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
