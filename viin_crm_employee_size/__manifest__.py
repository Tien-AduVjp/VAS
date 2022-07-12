{
    'name': "CRM - Employee Size",
    'name_vi_VN': "CRM - Quy Mô Nhân Viên",

    'summary': """
Add field 'Employee size' to CRM form""",

    'summary_vi_VN': """
Thêm trường 'Quy mô nhân viên' trên form CRM""",

    'description': """
What it does
============
Add the 'Employee Size' field including a title and description to CRM form for users to have a better understanding of their customer persona.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Thêm trường 'Quy mô nhân viên' bao gồm tiêu đề và mô tả vào biểu mẫu CRM để người dùng hiểu rõ hơn về chân dung khách hàng của họ.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Sales/CRM',
    'version': '0.1',
    'depends': ['crm', 'to_partner_employee_size'],
    'data': [
        'views/crm_lead_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
