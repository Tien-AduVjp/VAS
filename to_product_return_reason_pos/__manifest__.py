# -*- coding: utf-8 -*-

{
    'name': 'Product Return Reasons - Point of Sales',
    'name_vi_VN': 'Lý do trả hàng - Điểm Bán Lẻ',

    'summary': 'Add reason for return products in PoS',
    'summary_vi_VN': 'Thêm lý do trả hàng cho điểm bán lẻ',

    'description': """
Summary
=======

Extending the application `Return in Point of Sales Screen` (to_pos_frontend_return) and the application `Product Return Reasons - Inventory`
(to_product_return_reason_stock) to allows PoS users to specify a reason for Point of Sales order return without leaving PoS screen

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tổng quan
=========

Mở rộng ứng dụng `Trả Hàng Ngay Trên Màn Hình PoS` (to_pos_frontend_return) và ứng dụng `Lý Do Trả Hàng - Hàng Tồn Kho`
(to_product_return_reason_stock) cho phép người dùng PoS chỉ định lý do trả hàng cho điểm bán lẻ mà không cần rời khỏi màn hình PoS

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'version': '1.0.1',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Point of sale',
    'depends': ['to_product_return_reason_stock', 'to_pos_frontend_return'],
    'data': [
            'security/module_security.xml',
            'views/assets.xml',
            'views/menu.xml',
            'views/pos_order_view.xml',
            'views/pos_config_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'qweb': [
        'static/src/xml/ReturnOrder/ReturnOrderLine.xml',
        'static/src/xml/ReturnOrder/ReturnOrderScreen.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 49.5,
    'currency': 'EUR',
    'license': 'OPL-1',
}
