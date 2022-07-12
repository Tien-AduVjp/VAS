# -*- coding: utf-8 -*-

{
    'name': 'Tracking PoS Return with Return Origin',
    'name_vi_VN': 'Theo dõi đơn trả hàng từ đơn hàng gốc (POS)',
    'version': '1.0.0',
    'category': 'Point of Sale',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 6,
    'summary': 'Link PoS return order to its original',
    'summary_vi_VN': 'Liên kết đơn trả hàng với đơn hàng gốc (trong POS)',
    'description': """
What it does
============

1. Track down all the Return Orders of a PoS Order
2. Track up the source/origin order from which the return order come

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Module này làm gì
=================

1. Theo dõi tất cả đơn trả hàng của đơn hàng PoS
2. Truy vết đơn hàng gốc mà đơn trả hàng được tạo từ đó

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
