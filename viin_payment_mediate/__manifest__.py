{
    'name': "Form Payment Extend",
    'name_vi_VN': "Mở rộng Form Thanh toán",

    'summary': """
Add notebook tag to payment form view
""",
    'summary_vi_VN': """
Tạo thẻ notebook trên form Thanh toán.
""",

    'description': """
What it does
============
Add notebook tag to payment form view for others to inherit and inject pages inside.

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
Thêm thẻ notebook vào form Thanh toán để phục vụ các module về sau cho nhu cầu thêm page vào form này.

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
    'category': 'Hidden',
    'version': '0.1.0',
    'depends': ['account'],

    'data': [
        'views/account_payment_views.xml'
        ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
