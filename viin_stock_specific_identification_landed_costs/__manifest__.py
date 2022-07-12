{
    'name': "Stock Specific Identification & Landed Costs",
    'name_vi_VN': "Thực tế Đích danh Kho & Chi phí về Kho",

    'summary': """
Allow landed costs can be applied for products with automated inventory valuation and specific identification costing method""",

    'summary_vi_VN': """
Cho phép chi phí về kho có thể được áp dụng cho các sản phẩm sử dụng định giá hàng tồn kho tự động và phương pháp thực tế đích danh
    	""",

    'description': """
What it does
============
This module allows landed costs can be applied for products with automated inventory valuation and specific identification costing method

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này cho phép chi phí về kho có thể được áp dụng cho các sản phẩm sử dụng định giá hàng tồn kho tự động và phương pháp thực tế đích danh

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
    'category': 'Operations/Inventory/Accounting',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs', 'viin_stock_specific_identification'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
