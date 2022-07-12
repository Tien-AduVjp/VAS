{
    'name': "Event Timesheet",
    'name_vi_VN': "Chấm công trên sự kiện",
    'summary': "Integrate Timesheet application with Event application",
    'summary_vi_VN': "Tích hợp ứng dụng chấm công với sự kiện.",

    'description': """
What it does
============
This module allow attendees log timesheet per event.

Key Features
============
1. Allow timekeeping directly on the Event.
2. Add a report of time related to the this event.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô-đun này cho phép người tham dự có thể chấm công trên từng sự kiện mà mình tham gia.

Tính năng chính
===============
1. Cho phép chấm công trực tiếp trên Sự kiện.
2. Thêm báo cáo về thời gian liên quan đến sự kiện đó.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resource',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_event_project', 'hr_timesheet'],

    # always loaded
    'data': [
        'views/event_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
