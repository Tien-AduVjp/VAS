{
    'name': "Stock Internal Transit Valuation - Specific Identification",
    'name_vi_VN': "Thực tế đích danh với Chuyển kho nội bộ",
    
    'summary': """
Extending Transit Location Accounting module to support specific identification valuation method""",
    'summary_vi_VN': """
Mở rộng module Tài Khoản Địa Điểm Chuyển Tiếp để hỗ trợ phương pháp định giá tồn kho theo thực tế đích danh
""",

    'description': """
What it does
============
Extending Transit Location Accounting module to support specific identification valuation method

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mở rộng module Tài Khoản Địa Điểm Chuyển Tiếp để hỗ trợ phương pháp định giá tồn kho theo thực tế đích danh

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
    'depends': ['to_transit_loc_accounts', 'viin_stock_specific_identification'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
