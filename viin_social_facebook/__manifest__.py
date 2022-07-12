{
    'name': "Facebook Social Marketing",
    'name_vi_VN': "Facebook Social Marketing",

    'summary': """
Integration with Facebook
""",

    'summary_vi_VN': """
Tích hợp với Facebook
""",

    'description': """
What it does
============
This module allows you to integrate with Facebook for on-system management.

Key Features
============
#. Manage Facebook media
#. Management of social networking Pages

   * Synchronize data of social networking pages

#. Manage the posts on the system

   * Allows one post to be posted on multiple social networking pages
   * Post scheduled

#. Manage posts on the system

   * Data synchronization
   * Post, Edit, Delete posts.
   * Receive, Reply, Delete Comment.

#. Manage user interactions

   * Manage user interaction notifications
   * Manage user messages

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Module này cho phép bạn tích hợp với Facebook để quản lý trên hệ thống.

Tính năng nổi bật
=================
#. Quản lý phương tiện truyền thông Facebook
#. Quản lý các trang mạng xã hội

   * Đồng bộ dữ liệu của các trang mạng xã hội
   * Cập nhật cài đặt trang xã hội

#. Quản lý các bài viết trên hệ thống

   * Cho phép một bài viết có thể được đăng trên nhiều trang mạng xã hội
   * Tạo lịch đăng bài

#. Quản lý các bài đăng trên hệ thống

   * Đồng bộ dữ liệu
   * Đăng, Sửa, Xóa bài đăng.
   * Nhận, Trả lời, Xóa bình luận.

#. Quản lý tương tác người dùng

   * Quản lý thông báo tương tác của người dùng
   * Quản lý tin nhắn của người dùng

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Social Marketing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_social'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/media_data.xml',
        'views/assets.xml',
        'views/res_config_settings_views.xml',
        'views/social_media_views.xml',
        'views/social_page_views.xml',
        'views/social_article_views.xml',
        'views/social_post_views.xml',
        'views/social_facebook_preview_templates.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 198.9,
    'subscription_price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
