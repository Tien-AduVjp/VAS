# -*- coding: utf-8 -*-

{
    'name' : 'Product Weekday Pricelist',
    'name_vi_VN':'Bảng giá Sản phẩm theo Ngày trong Tuần',

    'summary': 'Add different pricing for days of week',
    'summary_vi_VN':'Điều chỉnh giá tùy theo ngày trong tuần',

    'description':"""
Summary
=======

Pricelist Items can now apply to a specific day of week (e.g. Discount 5% on Saturday, Discount 7% on Sunday, etc).

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tổng quan
=========

Bảng giá sản phẩm có thể áp dụng cho ngày cụ thể trong tuần (vd. Giảm giá 5% vào thứ Bảy, Giảm giá 7% vào Chủ nhật, vv).

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'version': '1.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 30,
    'category': 'Sales',
    'depends': ['product'],
    'data': [
             'views/product_pricelist_item_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
