{
    'name': "Preventive Maintenance Mode",
    'name_vi_VN': "Chế độ bảo trì phòng ngừa",

    'summary': """
Module to add a field to distinguish preventive maintenance mode with other integrated modules
    """,
    'summary_vi_VN': """
Mô-đun thêm một trường để phân biệt chế độ bảo trì phòng ngừa mặc định với các mô-đun tích hợp khác
    """,

    'description': """
What it does
============
Add a field to distinguish preventive maintenance mode with other integrated modules.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thêm trường để phân biệt chế độ bảo trì phòng ngừa mặc định với những chế độ của mô-đun tích hợp khác.

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
    'category': 'Human Resources',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

    # always loaded
    'data': [
        'views/maintenance_equipment_views.xml',
    ],
    'pre_init_hook':'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
