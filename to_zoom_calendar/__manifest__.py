{
    'name': "Zoom Calendar Integration",
    'name_vi_VN': "Tích Hợp Zoom với Calendar",

    'summary': """
Zoom & Calendar Integration
""",

    'summary_vi_VN': """
Tích Hợp Zoom với Calendar
        """,

    'description': """
What it does
============
* This module allows users to integrate Zoom with the Calendar.

Key Features
============
* An option of Zoom meeting is offered as you create a meeting on Calendar.
* By choosing this option, a Zoom meeting is scheduled and the link to the meeting are shown on the calendar.
* Sending emails to the meeting attendees.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Module này cho phép bạn tích hợp Zoom với Lịch.

Tính năng nổi bật
=================
* Khi tạo lịch sẽ có tùy chọn để đánh dấu cuộc họp này sẽ diễn ra trên Zoom.
* Nếu chọn tùy chọn này, một cuộc họp trên Zoom sẽ được tạo, link đến cuộc họp sẽ được lưu trên lịch.
* Gửi email thông báo đến những người tham dự link vào zoom meeting.

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
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['calendar', 'to_base'],
    'external_dependencies' : {
        'python' : ['PyJWT'],
    },
    'data': [
        'security/zoom_calendar_security.xml',
        'security/ir.model.access.csv',
        'data/mail_data.xml',
        'views/calendar_event_view.xml',
        'views/zoom_calendar_menu.xml',
        'views/res_config_settings_view.xml',
        'views/calendar_templates.xml',
        'views/zoom_user_view.xml',
        'wizard/zoom_user_report_view.xml',
        'report/zoom_user_report.xml',
        ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 288.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
