{
    'name': "Helpdesk Timesheet Integration",
    'name_vi_VN': "Tích hợp ứng dụng Trung Tâm Hỗ Trợ với Chấm Công",

    'summary': """
Helpdesk Timesheet Integration
""",

    'summary_vi_VN': """
Tích hợp ứng dụng Trung Tâm Hỗ Trợ với Chấm Công
""",

    'description': """
Key Features
============
* Track the customer care time and progress of the support team
* A project can be assigned to a support channel of a team, the purpose of this is to link a support ticket to a project task and log timesheet for that task.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Theo dõi thời gian và tiến tình chăm sóc khách hàng của đội ngũ hỗ trợ
* Có thể gán một dự án tới một kênh hỗ trợ do một đội phụ trách, mục đích là liên kết một đề xuất hỗ trợ với một nhiệm vụ dự án và ghi nhận chấm công theo thời gian cho nhiệm vụ đó.

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
    'category': 'Helpdesk',
    'version': '0.2.1',
    'depends': ['viin_helpdesk', 'hr_timesheet'],
    'data': [
        'security/module_security.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/project_project_views.xml',
        'wizards/task_to_ticket_wizard_views.xml',
        'views/project_task_views.xml',
        'reports/report_helpdesk_ticket_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
