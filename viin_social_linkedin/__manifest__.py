{
    'name': "Linkedin Social Marketing",
    'name_vi_VN': "Linkedin Social Marketing",

    'summary': """
Integration with Linkedin
""",

    'summary_vi_VN': """
Tích hợp với Linkedin
""",

    'description': """
What it does
============
This module allows you to integrate with Linkedin for on-system management.

Key Features
============
#. Manage Linkedin media
#. Management of social networking Pages

   * Synchronize data of social networking pages

#. Manage the articles on the system

   * Allows to be posted on multiple social networking pages

#. Manage posts on the system

   * Data synchronization
   * Post, Edit, Delete posts.
   * Receive, Reply, Delete Comment.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này cho phép bạn tích hợp với Linkedin để quản lý trên hệ thống.

Tính năng chính
===============
#. Quản lý phương tiện truyền thông Linkedin
#. Quản lý các trang mạng xã hội

   * Đồng bộ dữ liệu của các trang mạng xã hội

#. Quản lý các bài viết trên hệ thống

   * Cho phép một bài viết có thể được đăng trên nhiều trang mạng xã hội

#. Quản lý các bài đăng trên hệ thống

   * Đồng bộ dữ liệu
   * Đăng, Sửa, Xóa bài đăng.
   * Nhận, Trả lời, Xóa bình luận.

Ấn bản được hỗ trợ
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
        'data/media_data.xml',
        'views/assets.xml',
        'views/res_config_settings_views.xml',
        'views/social_media_views.xml',
        'views/social_page_views.xml',
        'views/social_linkedin_preview_templates.xml',
        'views/social_article_views.xml',
        'views/social_post_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
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
