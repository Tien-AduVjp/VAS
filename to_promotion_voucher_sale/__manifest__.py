# -*- coding: utf-8 -*-

{
    'name' : 'Promotion Vouchers - Sales Management Integration',
    'name_vi_VN': 'Tích hợp phiếu khuyến mãi - Bán hàng',
    'summary': 'Sell promotion vouchers using Sales Management apps',
    'summary_vi_VN': 'Bán phiếu khuyến mãi sử dụng ứng dụng Bán hàng',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Sales',
    'description':"""
What it does
============
This module integrates Sales Management application and Promotion Voucher application to allows you to sell promotion vouchers using Sales Management apps

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Mô tả
=====
Mô-đun này tích hợp hai ứng dụng Bán hàng và Phiếu khuyến mãi, cho phép bán phiếu khuyến mãi ở ứng dụng bán hàng

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['to_promotion_voucher', 'sale_stock'],
    'data': [
        'data/menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
