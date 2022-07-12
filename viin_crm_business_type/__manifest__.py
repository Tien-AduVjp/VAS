{
    'name': "CRM - Business Type",
    'name_vi_VN': "CRM - Loại Hình Doanh Nghiệp",

    'summary': """
Add field 'Business type' to CRM form""",

    'summary_vi_VN': """
Thêm trường 'Loại hình doanh nghiệp' trên form CRM""",

    'description': """
What it does
============
Add the 'Business Type' field including a name and description to CRM form for users to have a better understanding of their customer persona.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Thêm trường 'Loại hình doanh nghiệp' bao gồm tên và mô tả vào biểu mẫu CRM để người dùng hiểu rõ hơn về chân dung khách hàng của họ.

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
    'category': 'Sales/CRM',
    'version': '0.1',
    'depends': ['crm', 'to_partner_business_type'],
    'data': [
        'views/crm_lead_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'pre_init_hook': 'pre_init_hook',
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
