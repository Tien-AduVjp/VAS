# -*- coding: utf-8 -*-
{
    'name': "BoM Component Cost Percentage",
    'name_vi_VN': "Phần trăm giá vốn các thành phần trong Định mức Nguyên vật liệu",

    'summary': """Devide the price percentage for the components in BOM.
        """,

    'summary_vi_VN': """
Chia tỉ lệ phần trăm giá trị cho các thành phần của Định mức Nguyên vật liệu.
        """,

    'description': """
What it does
============
* For equipment products: if you want to unbuild and sell the equipment by component, use the FIFO cost method when receiving.
* When receiving a synced equipment, the cost price is counted on the entire equipment.
* When unbuilding a equipment, you need to set the price for each component to define its cost price.

Key Features
============
* Define cost percentage for components of the equipment/product based on its Bills of Materials.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Với hàng hóa là máy móc thiết bị khi nhập kho sử dụng phương pháp giá thực tế đích danh hoặc trung bình,nếu doanh nghiệp có nhu cầu tháo dỡ để bán từng thành phần
* Khi nhập hàng một thiết bị đồng bộ, giá vốn được tính trên toàn bộ thiết bị
* Khi tách ra thành các thành phần của thiết bị, cần định giá cho từng thành phần phục vụ cho việc tính toán giá vốn của phụ kiện, thành phần đó.

Tính năng nổi bật
=================
* Ấn định tỷ lệ chia phần trăm giá vốn cho các thành phần của thiết bị/ sản phẩm dựa trên định mức nguyên vật liệu (BOM) cho thiết bị đó.

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

    'depends': ['mrp'],

    'data': [
        'views/mrp_bom.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
