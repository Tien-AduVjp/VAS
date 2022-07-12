{
    'name': "Viindoo Mobile Notification",
    'name_vi_VN': "Thông báo Di động",
    'version': '0.1.1',
    'summary': """Notification feature for mobile app""",
    'summary_vi_VN': """
Chức năng thông báo cho ứng dụng di động
    	""",
    'sequence': '11',
    'description': """
What it does
============
This is the base module for sending notifications to mobile application. This module needs to be extended by other modules to be able to connect with different notification service providers.


Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Đây là module cơ sở cho việc gửi thông báo qua ứng dụng di động, và cần được mở rộng thông qua các module khác để có thể kết nối với các nhà cung cấp dịch vụ thông báo khác nhau

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,
    'author': "Viindoo Technology Joint Stock Company",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'depends': ['mail'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'data/resend_notification.xml',
        'views/res_partner_token.xml',
        'views/mobile_notifications_view.xml',
        'views/res_config_settings_views.xml',
        'views/mail_channel_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
