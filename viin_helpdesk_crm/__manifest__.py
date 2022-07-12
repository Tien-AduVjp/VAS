{
    'name': "Helpdesk CRM Integration",
    'name_vi_VN': "Tích hợp Helpdesk với CRM",

    'summary': """
Helpdesk CRM Integration
""",

    'summary_vi_VN': """
Tích hợp Helpdesk với CRM
""",

    'description': """
What it does
============
This module integrates Helpdesk and CRM apps to optimize the customer relationship management process

Key Features
============
* Create a new ticket and attach it to an Opportunity
* Convert Lead/Opportunity into Tickets
* By creating tickets, you can select or create a new Lead/Opportunity to attach to the ticket itself
* Allow providing Lead/Opportunity information to the tickets report to calculate the number of tickets assigned to each Lead/Opportunity

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này tích hợp ứng dụng Trung Tâm Hỗ Trợ và Quản Trị Quan Hệ Khách Hàng (CRM) để tối ưu hóa quy trình quản lý quan hệ khách hàng

Tính năng nổi bật
=================
* Tạo Yêu cầu hỗ trợ mới và gắn nó vào Cơ hội
* Chuyển đổi Tiềm năng/Cơ hội thành Yêu cầu hỗ trợ
* Từ phần Yêu cầu hỗ trợ, có thể chọn hoặc tạo mới 1 Tiềm năng/Cơ hội để gắn vào chính phiếu đó
* Bổ sung thông tin Tiềm năng/Cơ hội vào báo cáo của Yêu cầu hỗ trợ để thống kê được số lượng Yêu cầu hỗ trợ gán với từng Tiềm năng/Cơ hội

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Helpdesk',
    'version': '0.1',
    'depends': ['viin_helpdesk', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/crm_lead_to_ticket_wizard_views.xml',
        'views/crm_lead_views.xml',
        'views/helpdesk_ticket_views.xml',
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
