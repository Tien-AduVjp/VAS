{
    'name': "Event Project",
    'name_vi_VN': "Tích hợp dự án với sự kiện",
    'summary': "Link Event to Project",
    'summary_vi_VN': "Liên kết Sự kiện với Dự án",
    'description': """
What it does
============
This is base module to link Event to Projects.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Đây là mô đun cơ sở, nhằm tạo ra liên kết giữa Sự kiện với Dự án.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project', 'event'],

    # always loaded
    'data': [
        'views/event_views.xml',
        'views/project_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
