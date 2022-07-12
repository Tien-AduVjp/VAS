# -*- coding: utf-8 -*-

{
    'name' : 'Sales - POS Voucher',
    'name_vi_VN': 'Sales - POS Voucher',
    'summary': 'Integrate Promotion voucher with both of POS and Sales APP',
    'summary_vi_VN': 'Tích hợp phiếu khuyến mại với cả POS và Sales',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Sales',
    'description':"""
What is does
============
This module fixes the problem when Promotion Vouchers are integrated with both Sales & Point of Sales Applications

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Mô tả
=====
Mô-đun này giải quyết các vấn đề gặp phải khi ứng dụng Phiếu khuyến mãi được tích hợp với cả ứng dụng Bán hàng và Điểm bán lẻ

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['to_promotion_voucher_pos', 'to_promotion_voucher_sale'],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
