{
    'name': "Forum - Security Groups",
    'name_vi_VN': "Phân quyền cho Diễn đàn",

    'summary': "Provides security groups with different levels of permissions for forum feature.",
    'summary_vi_VN': "Cung cấp các nhóm quyền với các cấp quyền hạn khác nhau cho tính năng diễn đàn",

    'description': """
What it does
============
This module provides 2 new security groups for Forum feature:

   - Forum/All Forums Moderator: Have full permissions on all forums, except configuring forum's settings.
   - Forum/Administrator: Have full permissions on all forums, include configuring moderators and other 
     settings.

You can also manually add moderators for each forum in its configuration.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô đun này cung cấp thêm 2 nhóm phân quyền cho tính năng Diễn đàn:

   - Diễn đàn/Điều hành tất cả diễn đàn: Có toàn quyền trên tất cả các diễn đàn, trừ việc cấu hình chúng.
   - Diễn đàn/Quản trị viên: Có toàn quyền trên tất cả các diễn đàn, bao gồm cả việc cấu hình người điều hành
     và các thiết lập khác.

Bạn cũng có thể thêm thủ công người điều hành cho từng diễn đàn ở phần thiết lập của diễn đàn đó.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author' : 'Viindoo',
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 100,
    'category': 'Website/Forum',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_forum'],

    # always loaded
    'data': [
          'security/module_security.xml',
          'security/ir.model.access.csv',
          'views/forum_forum_views.xml',
          'views/menu.xml',
          'views/forum_template.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
