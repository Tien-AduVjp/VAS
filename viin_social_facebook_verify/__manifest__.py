{
    'name': "Facebook: Convert Long-lived Token",
    'name_vi_VN': "Facebook: Chuyển đổi mã dài hạn",

    'summary': """
Convert access token from 1h to 60 days token
""",

    'summary_vi_VN': """
Chuyển đổi mã truy cập ngắn hạn (1h) sang mã dài hạn (60 ngày)
""",

    'description': """
Key Features
============
* If your Facebook app is not verified yet and without access to get Page information, you will have to use the 1 hour validation Access Token on "Graph API Explorer".
* Therefore, this module allows you to convert short-term (1h) to long-term access codes (60 days) for continuous use.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Nếu ứng dụng Facebook của bạn chưa được xác minh và không có quyền truy cập để lấy thông tin Trang, bạn sẽ phải sử dụng Mã truy cập xác thực chỉ có hiệu lực 1 giờ trên "Graph API Explorer".
* Vì vậy, module này cho phép bạn chuyển đổi mã truy cập ngắn hạn (1h) sang dài hạn (60 ngày) để sử dụng liên tục.

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Social Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_social_facebook'],

    # always loaded
    'data': [
        'views/social_media_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price':45.9,
    'subscription_price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
