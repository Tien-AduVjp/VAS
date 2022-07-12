{
    'name' : 'Payment Terms Extended',
    'name_vi_VN' : 'Điều khoản thanh toán mở rộng',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': 'Extend Payment Terms',
    'summary_vi_VN': 'Mở rộng điều khoản thanh toán',
    'sequence': 24,
    'category': 'Accounting',
    'description':"""
Key Features
============
Allow to configure the due date in Payment Terms with

  * Fixed Day of Next X Month(s)
  * Last Day of Next X Month(s)

*Where X is a number of months defined by the users.*

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
'description_vi_VN': """
Tính năng nổi bật
=================
Cho phép cấu hình ngày dến hạn trong điều khoản thanh toán với:

  * Ngày cố định của X tháng kế tiếp
  * Ngày cuối của X tháng kế tiếp

*Trong đó X là số tháng được xác định bởi người dùng.*

Ấn bản được hỗ trợ
===================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'depends': ['account'],
    'data': [
        'views/account_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
