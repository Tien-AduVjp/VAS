# -*- coding: utf-8 -*-
{
    'name': "Purchase BOM Stock Value",

    'summary': """Calculate cost for component products when using Bom Kit in purchase order.
        """,

    'summary_vi_VN': """Tính giá vốn cho các sản phẩm phụ kiện khi mua hàng theo Bom Kit.
        """,

    'description': """
What it does
============
* By default, when buying Kit products with bills of materials, the system will only caculate the Kit product's cost while the default component product's cost is 0.
* There is nothing wrong if you sell full set of product. However, when you sell each of component product, the system has no basis to caculate each of component product's cost.
* This module helps to set the price percentage for each component product (thanks to the module named "to_mrp_bom_component_percentage").
* Then the component product's cost wil be automatically caculated.

Key features
============
* When creating a purchase order with products set as a Kit with bills of materials, there will be receipts created for components of Kit.
* Automatically caculate cost for component products if Kit's price percentage has been set for each component product.

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
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
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
