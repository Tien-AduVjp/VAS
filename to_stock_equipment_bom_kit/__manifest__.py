# -*- coding: utf-8 -*-
{
    'name': "Stock Equipment Bom Kit",
    'name_vi_VN': "Tích hợp Thiết bị theo bộ và Kho",

    'summary': """
Generate child equipments (parts) from the parent that has Bom kit specified
        """,

    'summary_vi_VN': """
Tạo thiết bị con từ thiết bị cha có thiết lập Bom Kit
        """,

    'description': """
What it does
============

when buying a complete equipment that has BoM Kit specified, if enabled, its parts will be generated automatically as child equipments
according to the BoM Kit

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Khi mua sản phẩm đồng bộ đã được thiết lập Bom Kit, nếu tạo thiết bị từ sản phẩm này, hệ thống sẽ đưa ra các tùy chọn xem có
tạo các thiết bị khác là các thành phần trong Bom Kit hay không. Các thiết bị được tạo ra từ các thành phần trong Bom Kit sẽ
có quan hệ cha con với thiết bị được tạo từ đơn hàng mua.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'http://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_equipment', 'to_equipment_hierarchy', 'purchase_mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/product_set_line_views.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
