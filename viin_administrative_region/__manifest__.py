{
    'name': "Administrative Region Management",
    'name_vi_VN': "Quản lý Vùng Hành Chính",

    'summary': """Manage country's administrative regions which may differ from country's geographic regions in some countries""",
    'summary_vi_VN': """Quản lý vùng hành chính quốc gia, có thể khác với các vùng địa lý ở một số quốc gia""",

    'description': """
What it does
============
The module provides administrative region management features.

Key Features
============
* Administrative region management
* Default data for administrative regions in Vietnam. Others' can be added manually with the software UI.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Phân hệ cung cấp tính năng quản lý Vùng hành chính

Tính năng nổi bật
=================
* Quản lý Vùng hành chính
* Nạp sẵn dữ liệu vùng hành chính cho Việt Nam. Vùng hành chính của các quốc gia khác (nếu áp dụng) có thể được thêm thủ công trong phần mềm)

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Tools',
    'version': '0.1.0',
    'depends': ['mail'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'data/administrative_region_data.xml',
        'views/administrative_region_views.xml',
        'views/res_country_views.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
