{
    'name': "Helpdesk Ticket Severity",
    'name_vi_VN': "Mức độ nghiêm trọng trên yêu cầu hỗ trợ",

    'summary': """
Allows to set severity on the helpdesk ticket.""",

    'summary_vi_VN': """
Cho phép thiết lập mức độ nghiêm trọng trên yêu cầu hỗ trợ.
        """,

    'description': """
Allows to set severity on the helpdesk ticket.

Key Features
============
* Allows to set severity on the helpdesk ticket.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Cho phép thiết lập mức độ nghiêm trọng trên yêu cầu hỗ trợ.

Tính năng chính
===============
* Cho phép thiết lập mức độ nghiêm trọng trên yêu cầu hỗ trợ.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Services/Helpdesk',
    'version': '0.1',
    'depends': ['viin_helpdesk'],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'reports/report_helpdesk_ticket_views.xml',
    ],
    'images' : [
        #'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
