{
    'name': "BoM Component Cost Percentage - Unbuild",
    'name_vi_VN': "Tỷ lệ phần trăm chi phí thành phần - Tháo dỡ",

    'summary': """Calculate stock valuation for the components during MRP unbuild.
        """,
    'summary_vi_VN': """
Tính giá vốn cho các thành phần khi thực hiện tháo dỡ sản phẩm.
        """,

    'description': """
Key Features
============
* This module depends on 'to_mrp_bom_component_percentage'.
* This module calculates cost price for the equipment components based on the fixed cost percentage on each line of its BOM.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Kết hợp với module 'to_mrp_bom_component_percentage'
* Dựa vào tỷ lệ giá vốn được ấn định trên từng dòng thể hiện trên BOM của thiết để chia giá vốn cho các thành phần của thiết bị đó.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Purchases',
    'version': '0.1',

    'depends': ['to_mrp_bom_component_percentage', 'stock_account'],

    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
