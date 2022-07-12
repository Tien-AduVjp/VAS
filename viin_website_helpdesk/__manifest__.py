# -*- coding: utf-8 -*-
{
    'name': "Website Helpdesk Integration",
    'name_vi_VN': "Tích hợp Helpdesk với Website",

    'summary': """
Extend Helpdesk (viin_helpdesk) module, user can create/send/discuss a ticket without sign in on website.
""",

    'summary_vi_VN': """
Giúp người dùng có thể tạo/gửi ticket từ giao diện website.
""",

    'description': """
What it does
============
* This module extend Helpdesk (viin_helpdesk) module, generate a new form on website.
* User can create and send a new ticket from website

Key Features
============
1. New "Create ticket form" on webiste interface.
2. User can create/send/discuss ticket without sign in.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Kế thừa từ module Helpdesk, ứng dụng sẽ tạo giao diện ngoài website, cho phép người dùng tạo và gửi helpdesk ticket. 

Tính năng chính
===============
1. Giao diện form "Gửi ticket" ngoài trang web.
2. Người dùng có thể tạo, gửi, và trao đổi về ticket, mà không cần phải đăng nhập.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Website',
    'version': '0.2',
    'depends': ['website','viin_helpdesk','to_website_recaptcha'],
    'data': [
        'data/mail_template_data.xml',
        'data/website_menu_data.xml',
        'views/helpdesk_team_views.xml',
        'templates/website_helpdesk_template.xml',
    ],
    'demo': [
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
