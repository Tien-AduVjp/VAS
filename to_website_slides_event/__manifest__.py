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
* This module use event to organize and manage eLearning courses.
* Track trainers and trainees per event.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
* Mô đun này sử dụng sự kiện để tổ chức và quản lý các khóa học trực tuyến
* Theo dõi người giảng dạy và người tham gia trên từng sự kiện
    
Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
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
