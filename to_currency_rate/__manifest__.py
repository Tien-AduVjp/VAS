# -*- coding: utf-8 -*-

{
    'name' : 'Currency Rates Inverse',
    'name_vi_VN' : 'Tỷ giá tiền tệ nghịch đảo',
    'version': '1.0.2',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Currency Inverse Rate; Add Graph View;',
    'summary_vi_VN': 'Tỷ giá nghịch đảo, Lịch sử tỷ giá;',
    'sequence': 30,
    'category': 'Accounting & Finance',
    'description':"""
Description
===========

* Add Inverse Rate which is in relation with the rate so that the user can input either the rate or the inverse rate which is at his choice for the same result
* Add currency rates graph view which is useful for currency rates analysis over the time

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN':"""
Mô tả
=====

* Thêm Tỷ lệ nghịch đảo liên quan đến tỷ lệ để người dùng có thể nhập tỷ lệ hoặc tỷ lệ nghịch tùy theo lựa chọn của mình cho cùng một kết quả
* Thêm chế độ xem biểu đồ tỷ giá tiền tệ rất hữu ích cho việc phân tích tỷ giá tiền tệ theo thời gian

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'depends': ['base'],
    'data': [
        'views/res_currency_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
