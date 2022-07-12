{
    'name': 'MRP Barcode',
    'name_vi_VN': 'Mã vạch sản xuất',
    'summary': 'Add barcode scanning support to manufacturing',
    'summary_vi_VN': 'Hỗ trợ quét mã vạch cho hệ thống sản xuất',
    'description': """
What it does
============
* This module adds support for barcodes scanning to the manufacturing system.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Hỗ trợ chức năng quét mã vạch cho hệ thống sản xuất.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA)',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Manufacturing',
    'version': '1.0',

    'depends': ['to_mrp_workorder', 'to_stock_barcode'],

    'data': [
        'views/mrp_workorder_views.xml',
        'views/mrp_workcenter_block_views.xml',
        'views/mrp_production_views.xml',
    ],
    'qweb': [
        "static/src/xml/mrp_barcode.xml",
    ],
    'demo': [
        'data/mrp_barcode_demo.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False, #Set True when upgrading to 14.0
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
