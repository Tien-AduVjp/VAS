# -*- coding: utf-8 -*-
{
    'name': "Purchase BoM Stock Value",

    'summary': """Calculate cost for component products when using kit-type BoM in purchase order.
        """,

    'summary_vi_VN': """Tính giá vốn cho các sản phẩm phụ kiện khi mua hàng theo BoM Kit.
        """,

    'description': """
What it does
============
* By default, when buying products as kit-type via Bill of Materials, the system only records the cost of the KIT products. All the component products in the BoM have the cost of 0 by default.
* It does not matter if you sell the whole set of product. However, when you sell the component products separately, the system has no basis to calculate the cost of each one of them.
* This module helps to set the price percentage for each component product in this for this purpose.(thanks to the module named "to_mrp_bom_component_percentage").
* Then the cost of the component product will be automatically calculated.

Key features
============
* When creating a purchase order with products set as a Kit-type via Bill of Materials, the receipts are created for the components of Kit.
* Automatically calculate cost for component products based on the percentage set on each of the product component, which are manually entered on the purchase order.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Theo mặc định, khi mua một sản phẩm dạng Bom Kit, hệ thống chỉ ghi nhận được giá vốn của bộ sản phẩm. Còn các thành phần trong bộ sẽ có giá vốn mặc định bằng 0.
* Nếu vẫn bán theo bộ thì không gặp vấn đề gì. Tuy nhiên, khi bán tách lẻ từng thành phần thì không có cơ sở để tính giá vốn cho từng sản phẩm thành phần đó.
* Mô-đun này giúp thiết lập tỉ lệ giá cho các thành phần trong bộ (nhờ vào module "to_mrp_bom_component_percentage").
* Từ đó hệ thống tự động tính toán giá vốn cho các thành phần trong bộ sản phẩm.

Tính năng nổi bật
=================
* Khi tạo đơn hàng mua có sản phẩm được thiết lập Bom Kit, hệ thống sẽ nhận hàng theo các thành phần cấu thành Bom Kit.
* Khi đó nếu trên Bom Kit có thiết lập tỉ lệ giá cho các thành phần, hệ thống sẽ tự động tính giá vốn cho các thành phần từ giá mua.

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

    'category': 'Manufacturing',
    'version': '0.1',

    'depends': ['purchase_mrp', 'to_mrp_bom_component_percentage'],

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
