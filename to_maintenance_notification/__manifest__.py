{
    'name': "Maintenance Notification",
    'name_vi_VN': "Thông Báo Bảo Trì",
    'summary': """
        Post notification prior to maintenance scheduled date
        """,

    'summary_vi_VN': """Gửi thông báo trước ngày bảo trì theo lịch được ấn định
        """,

    'description': """
What it does
============
Post notification prior to maintenance scheduled date that is based on equipment maintenance schedule, equipment working frequency and working starting date

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Cho phép thiết lập số ngày sẽ thông báo trước khi đến hạn bảo trì.
* Gửi email thông báo đến người chịu trách nhiệm khi đến hạn

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_equipment_woking_frequency', 'to_maintenance_request_simple_mediate', 'viin_maintenance_preventive_mode'],

    # always loaded
    'data': [
        'data/mail_template_data.xml',
        'data/scheduler_data.xml',
        'views/maintenance_request_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_equipment_category_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
