{
    'name': "E-learning Events",
    'name_vi_VN': "Sự kiện cho Học trực tuyến",

    'summary': """
Organize eLearning courses using event""",
    'summary_vi_VN': """
Tổ chức các khóa học trực tuyến sử dụng sự kiện""",

    'description': """
What it does
============
* Allows to link an online course to an event.
* Each course content can be linked to a time period in that event.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Cho phép gắn khóa học trực tuyến tới một sự kiện.
* Mỗi nội dung của khóa học có thể liên kết tới 1 khoảng thời gian trong sự kiện đó.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Website/Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_slides', 'website_event_track'],

    # always loaded
    'data': [
        'views/event_views.xml',
        'views/event_track_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
