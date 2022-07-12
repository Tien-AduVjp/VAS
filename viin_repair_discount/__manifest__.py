{
    'name': "Repair - Discount",
    'name_vi_VN': "Sửa chữa - Chiết khấu",

    'summary': """
Repair service discount""",

    'summary_vi_VN': """
Chiết khấu dịch vụ sửa chữa""",

    'description': """
What it does
============
This module allows to enter % discount on each repair line.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cho phép nhập % chiết khấu trên từng dòng sửa chữa.

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

    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    'depends': ['repair'],
    'data': [
        'views/repair_order_views.xml',
        'report/repair_templates_repair_order.xml'
    ],
    'demo': [],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
