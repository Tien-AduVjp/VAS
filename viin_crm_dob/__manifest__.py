{
    'name': "CRM Partner Date of Birth",
    'name_vi_VN': "Ngày sinh của đối tác trên Tiềm năng/Cơ hội",

    'summary': """
Manage partner birth date on lead/opportunity
""",

    'summary_vi_VN': """
Quản lý ngày sinh của đối tác trên tiềm năng/cơ hội
""",

    'description': """
What it does
============
Manage partner birth date on lead/opportunity

Key Features
============
- Add birth date field on lead/opportunity
- Add birth date search filter/group on lead/opportunity views

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Quản lý ngày sinh của đối tác trên tiềm năng/cơ hội

Tính năng chính
===============
- Bổ sung trường ngày sinh trên tiềm năng/cơ hội
- Thêm bộ lọc/nhóm tìm kiếm trên giao diện của tiềm năng/cơ hội

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

    'category': 'Sales/CRM',
    'version': '0.1.1',
    'depends': ['to_partner_dob', 'crm'],
    'data': [
        'views/crm_lead_views.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
