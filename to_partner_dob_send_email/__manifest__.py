{
    'name': "Auto Send Happy Birthday Email",
    'name_vi_VN': 'Tự Động Gửi Email Chúc Mừng Sinh Nhật',
    'summary': """
Automatically Send Happy Birthday Email to your partners""",
    'summary_vi_VN': """
Tự động gửi email chúc mừng sinh nhật đến đối tác của bạn""",
    'description': """
What it does
============
Automatically send Happy Birthday Email to your partners.

Key Features
============
* Define your own Happy Birthday Email templates and assign to your companies/ partners. These Email templates support to enrich:

  * Text
  * Images
  * Multi Language

* Switch On/ Off the function of Automatic Happy Birthday Email for the companies/ partners.
* Multi-company is fully  supported. In other words, you could define different email templates for the same partner for different companies.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
'description_vi_VN': """
Mô tả
=====
Tự động gửi email chúc mừng sinh nhật đến Đối tác của bạn.

Tính năng chính
===============
* Tùy chọn mẫu email chúc mừng sinh nhật của riêng bạn và gán cho công ty/ đối tác của bạn. Mẫu email này hỗ trợ:

  * Văn bản
  * Hình ảnh
  * Đa ngôn ngữ

* Lựa chọn bật/ tắt chức năng tự động gửi email chúc mừng sinh nhật cho công ty/ đối tác.
* Hỗ trợ đầy đủ môi trường đa công ty. Nói cách khác, với mỗi công ty trong hệ thống, bạn có thể thiết kế các mẫu email khác nhau cho cùng 1 đối tác ứng với các công ty khác nhau.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['to_partner_dob', 'mail'],

    # always loaded
    'data': [
        'data/scheduler_data.xml',
        'data/mail_template_data.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
