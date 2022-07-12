{
    'name': "Lead/Opportunity Customer Recognition",
    'name_vi_VN': "Nhận diện khách hàng ở Tiềm năng / Cơ hội",

    'summary': """
Automatic customer recognition for Lead/Opportunity
""",
    'summary_vi_VN': """
Nhận diện khách hàng tự động ở Tiềm năng/Cơ hội
""",

    'description': """
What it does
============
* Recognize customer on lead/opportunity based on email, phone, mobile after create new
* Add button 'Recognize Customer' on lead/opportunity form to recognize again after change information

Key Features
============


Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô đun này làm gì
=================
* Nhận diện khách hàng trên tiềm năng/cơ hội dựa vào thư điện tử, điện thoại, di động sau khi tạo mới
* Thêm nút 'Nhận diện khách hàng' trên form tiềm năng/cơ hội để người dùng nhận diện lại sau khi thay đổi thông tin

Tính năng nổi bật
=================


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
    'version': '0.1.0',
    'depends': ['crm'],

    'data': [
        'views/crm_lead_views.xml',
    ],

    'installable': True,  # TODO: Rename this module into `viin_crm_customer_recognition` in 15+
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
