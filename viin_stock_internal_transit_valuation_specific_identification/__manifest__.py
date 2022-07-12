{
    'name': "Stock Internal Transit Valuation - Specific Identification",
    'name_vi_VN': "Thực tế đích danh với Định Giá Chuyển Tiếp Kho",
    'old_technical_name': "viin_transit_loc_accounts_specific_identification",
    'summary': """
Extending Stock Internal Transit Valuation module to support specific identification valuation method""",
    'summary_vi_VN': """
Mở rộng module Định Giá Chuyển Tiếp Kho để hỗ trợ phương pháp định giá tồn kho theo thực tế đích danh
""",

    'description': """
What it does
============
Extending Stock Internal Transit Valuation module to support specific identification valuation method

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mở rộng module Định Giá Chuyển Tiếp Kho để hỗ trợ phương pháp định giá tồn kho theo thực tế đích danh

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

    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_stock_internal_transit_valuation', 'viin_stock_specific_identification'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
