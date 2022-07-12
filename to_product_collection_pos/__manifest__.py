# -*- coding: utf-8 -*-
{
    'name': "Point of Sales & Product Collection",
    'name_vi_VN':"Điểm bán lẻ và Bộ sưu tập Sản phẩm",

    'summary': """Integrate Product Collection for Point of Sales""",
    'summary_vi_VN':"""Tích hợp Bộ sưu tập Sản phẩm cho điểm bán lẻ""",

    'description': """
What it does
============
This module extends the application Product Collection to get integrated with Point of Sales for analyzing sales of
product collection done with Point of Sales application

1. Sales/Revenue by a product collection
2. Product Collection Sales over the period of time (i.e. Day, Week, Month, Year)
3. Product Collection Sales by Salesperson
4. Product Collection Sales by Point of Sales
5. Product Collection Sales by Point of Sales Session
6. Etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Mô tả
=====
Mô-đun này mở rộng chức năng Bộ sưu tập Sản phẩm tích hợp cho điểm bán lẻ để phân tích đơn hàng theo loại Sản phẩm
ở mỗi ứng dụng điểm bán lẻ

1. Đơn hàng/doanh thu theo loại sản phẩm
2. Phân loại sản phẩm theo thời gian (vd. Ngày, Tuần, Tháng, Năm)
3. Phân loại sản phẩm theo người bán
4. Phân loại sản phẩm theo điểm bán lẻ
5. Phân loại sản phẩm theo phiên điểm bán lẻ
6. v.v

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point of sale',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'to_product_collection'],

    # always loaded
    'data': [
        'views/product_collection_pos_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
