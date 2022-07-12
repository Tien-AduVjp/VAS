{
    'name': "Social Marketing",
    'name_vi_VN': "Social Marketing",

    'summary': """
Integration and Management of social networks.""",

    'summary_vi_VN': """
Tích hợp và quản lý các Mạng xã hội
    	""",

    'description': """
What it does
============
* Integration and Management of social networks.
* This module is the basis for modules related to another social network to inherit.

Key Features
============
#. Management of media

   * For example: Facebook, Linkedin, ...

#. Management of social networking pages

   * Synchronize data of social networking pages

#. Management of articles on the system

   * Allow articles to be posted on multiple social networking pages

#. Management of posts on the system

   * Synchronize data
   * Post, edit, delete posts.
   * Receive, reply, delete comments.

#. Management of user interaction notifications

   * Synchronize data
   * Allow receiving interaction notifications about the posts

#. Access rights

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Tích hợp và Quản lý các mạng xã hội.
* Module này là cơ sở để các module liên quan đến một mạng xã hội khác kế thừa vào.

Tính năng nổi bật
=================
#. Quản lý các phương tiện truyền thông

   * Ví dụ: Facebook, Linkedin,...

#. Quản lý các trang mạng xã hội

   * Đồng bộ dữ liệu của các trang mạng xã hội

#. Quản lý các bài viết trên hệ thống

   * Cho phép một bài viết có thể được đăng trên nhiều trang mạng xã hội

#. Quản lý các bài đăng trên hệ thống

   * Đồng bộ dữ liệu
   * Đăng, sửa, xóa bài đăng.
   * Nhận, trả lời, xóa bình luận.

#. Quản lý các thông báo tương tác người dùng

   * Đồng bộ dữ liệu
   * Cho phép nhận thông báo tương tác về các bài viết

#. Quyền truy cập

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com/intro/social-marketing",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Social Marketing',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'to_base', 'utm'],
    'qweb': [
        'static/src/xml/social_templates.xml',
        'static/src/xml/social_attachments_carousel.xml',
        'static/src/xml/post_detail.xml',
        'static/src/xml/social_post_button_synchronize.xml',
        'static/src/xml/social_notice_button_read_all.xml',
        'static/src/components/discuss_sidebar/discuss_sidebar.xml',
        'static/src/xml/attachment_preview.xml'
    ],
    # always loaded
    'data': [
        'security/social_security.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/root_menu.xml',
        'views/social_article_views.xml',
        'views/social_post_views.xml',
        'views/social_page_views.xml',
        'views/social_media_views.xml',
        'views/social_notice_views.xml',
        'views/res_config_settings_views.xml',
        'data/social_media_data.xml',
        'data/social_post_data.xml',
        'wizards/social_post_action_edit_post_view.xml',
        'wizards/wizard_social_confirm.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 198.9,
    'subscription_price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
