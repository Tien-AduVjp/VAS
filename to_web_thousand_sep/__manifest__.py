{
    'name': 'Web Thousand Separators',
    'name_vi_VN': 'Dấu phân cách hàng nghìn',
    'version': '0.1.0',
    'category': 'Productivity',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'sequence': 10,
    'summary': 'Format numbers with thousand separators on-fly.',
    'summary_vi_VN': 'Hiển thị dấu phân cách hàng nghìn ngay tại thời điểm nhập số liệu',
    'description': """

Key Features
============
In Odoo, it is default that thousand separators only appear after you finish typing. This module shows separators on-fly during your input while respecting user's language settings

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """

Mô tả
=====
Odoo mặc định chỉ hiển thị dấu phân cách hàng nghìn sau khi hoàn thành việc nhập số liệu. Mô-đun này để khắc phục điều đó, giúp hiển thị dấu phân cách ngay tại thời điểm nhập số liệu dựa trên thiết lập ngôn ngữ của người dùng.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'depends': ['web'],
    'data': [
        'views/header.xml'
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
