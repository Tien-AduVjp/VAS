# -*- coding: utf-8 -*-
{
    'name': "Helpdesk Livechat",
    'name_vi_VN': "Tích hợp ứng dụng Trung Tâm Hỗ Trợ với Chat trực tuyến",

    'summary': """
Create new helpdesk ticket with using /ticket command in the channel.
""",

    'summary_vi_VN': """
Tạo phiếu hỗ trợ mới bằng cách sử dụng câu lệnh /ticket từ một kênh bất kỳ.
""",

    'description': """
Key Features
============
* Allows creating Tickets directly by using /ticket command in the channel.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Cho phép tạo phiếu hỗ trợ trực tiếp bằng cách sử dụng câu lệnh /ticket từ một kênh bất kỳ.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Helpdesk',
    'version': '0.1',
    'depends': ['viin_helpdesk', 'im_livechat'],
    'data': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
