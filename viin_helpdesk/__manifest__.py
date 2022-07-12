# -*- coding: utf-8 -*-
{
    'name': "Helpdesk",
    'name_vi_VN': "Quầy hỗ trợ",

    'summary': """
Manage and track support tickets""",

    'summary_vi_VN': """
Quản lý và theo dõi các ticket.
    	""",

    'description': """
This app allow submit and follow helpdesk tickets

Key Features
============
* Can create Support Team, Ticket Type to categorize request of customer accordingly.
* Assign handling requests according to each member in each Team.
* Create support request from the Portal.
* Save history in Portal and Backend systems.
* Send Email when there is new feedback.
* Send Email for customer when change resolve phase.
* Rating from customers.
* Overall report all requests from customers.
* Is the base module for development and integration of Helpdesk with Sale, Website, Appstore.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này cho phép gửi và theo dõi các helpdesk ticket

Tính năng chính
===============
* Có thể tạo các Nhóm hỗ trợ, Kiểu ticket để phân loại yêu cầu của khách hàng cho phù hợp.
* Phân công xử lý các yêu cầu theo từng thành viên trong từng nhóm.
* Tạo yêu câu hỗ trợ từ Portal.
* Ghi nhận lịch sử liên lạc trong hệ thống Portal và Backend
* Gửi Email khi có phản hồi, liên lạc mới.
* Gửi Email cho khách hàng khi chuyển giai đoạn xử lý yêu cầu hỗ trợ
* Quản lý thời gian xử lý các yêu cầu.
* Đánh giá từ phía khách hàng
* Báo cáo tổng thể của các yêu cầu hỗ trợ từ khách hàng.
* Là module cơ sở để phát triển, tích hợp Helpdesk với Sale, Website, Appstore

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Operations/Helpdesk',
    'version': '0.8',
    'depends': ['portal', 'rating', 'digest'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/helpdesk_stage_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/helpdesk_ticket_type_data.xml',
        'data/rating_cron.xml',
        'data/digest_data.xml',
        'views/root_menu.xml',
        'views/digest_digest_views.xml',
        'views/helpdesk_assets.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_type_views.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_stage_views.xml',
        'views/helpdesk_tag_views.xml',
        'views/rating_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/helpdesk_sla_views.xml',
        'reports/report_helpdesk_ticket_views.xml',
        'reports/report_helpdesk_sla_views.xml',
        'templates/ticket_rating_templates.xml',
        'templates/team_rating_templates.xml',
        'templates/portal_templates.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
