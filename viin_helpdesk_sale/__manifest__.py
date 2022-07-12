# -*- coding: utf-8 -*-
{
    'name': "Helpdesk & Sale Integrator",
    'name_vi_VN': "Tích hợp ứng dụng Trung Tâm Hỗ Trợ & Bán hàng",

    'summary': """
Ticket management from customers who already have a Sale Order.
""",

    'summary_vi_VN': """
Quản lý đề xuất hỗ trợ từ khách hàng mà đã có Đơn hàng bán.
""",

    'description': """
What it does
============
* During the sales process, customer problems may require the support from other departments besides the sales department.
* This feature allows customers or sales staff to create support tickets to other departments on the Sales Order interface.

Key Features
============
* Allow customers to create support tickets directly from Portal and track the problem solving progress on Tickets
* When creating a new Ticket from SO, automatically check and assign to Helpdesk Sales teams
* Link SO to the Tickets has created from this SO
* Link Ticket to SO if this Ticket has created from SO

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Trong quá trình bán hàng, các vấn đề phát sinh của khách hàng có thể cần sự hỗ trợ của những bộ phận khác ngoài bộ phận kinh doanh.
* Tính năng này cho phép khách hàng hoặc nhân viên kinh doanh có thể tạo các phiếu yêu cầu hỗ trợ tới các bộ phận khác trên giao diện Đơn hàng bán
    
Tính năng nổi bật
=================

* Cho phép khách hàng tạo Phiếu hỗ trợ trực tiếp từ Cổng thông tin và theo dõi tiến trình giải quyết công việc trên các Phiếu hỗ trợ
* Khi tạo mới Phiếu hỗ trợ từ Đơn Bán, tự động kiểm tra và phân công cho Đội Ngũ Hỗ Trợ Kinh Doanh
* Liên kết Đơn Bán với Phiếu hỗ trợ được tạo từ chính đơn này
* Liên kết Phiếu hỗ trợ với Đơn Bán nếu phiếu đó được tạo từ đơn này

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
    'version': '0.1',
    'depends': ['viin_helpdesk', 'sale'],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'views/sale_order_views.xml',
        'views/sale_portal_templates.xml',
        'views/portal_template.xml',
        'report/report_helpdesk_ticket_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
