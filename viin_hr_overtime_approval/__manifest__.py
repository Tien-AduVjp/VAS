{
    'name': "Overtime Approval",
    'name_vi_VN': "Phê duyệt Tăng ca",

    'summary': """
Integrate applications Overtime Management and Approval for overtime approval process""",

    'summary_vi_VN': """
Tích hợp ứng dụng Tăng ca với ứng dụng Phê duyệt để cho phép phê duyệt các đề nghị tăng ca
    	""",

    'description': """
Key Features
============
This module allows users to approve the overtime registerations which can help to make an overtime plan:

    * Employee or Department Manager can register overtime plan for each and every employee in the company
    * Once registered, a overtime approval request is generated and sent to the mentioned employee's manager and HR Officer

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Mô-đun này cho phép người dùng phê duyệt các đơn đề xuất tăng ca, từ đó hỗ trợ việc lên kế hoạch tăng ca:

    * Nhân viên hoặc quản lý các phòng có thể đăng ký kế hoạch làm thêm giờ mình hoặc cho các nhân viên trong phòng ban
    * Sau khi đăng ký, một yêu cầu phê duyệt tăng ca sẽ được tạo và gửi đến Quản lý của nhân viên trên và Cán bộ phụ trách nhân sự

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Human Resources/Overtime',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['to_approvals', 'viin_hr_overtime'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/approval_request_type_views.xml',
        'views/approval_request_views.xml',
        'views/hr_overtime_plan_views.xml',
        'wizard/hr_overtime_request_mass_views.xml',
        'report/hr_employee_overtime_views.xml',
    ],

    # only loaded in demonstration mode
    'demo':[
    ],

    'images': [
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
