{
    'name': "Maintenance By Working Hours",

    'summary': """Maitenance by working hours
        """,

    'summary_vi_VN': """Bảo trì thiết bị theo giờ máy chạy
        """,

    'description': """
What it does
============
* Allow user to declare average daily working hours and working hours between each preventive maintenance for equipments
* Compute automatic the next maintenance date

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Cho phép khai báo số giờ chạy trung bình hàng ngày của thiết bị, số giờ chạy của thiết bị giữa các giai đoạn bảo trì.
* Tự động tính toán ngày cần thực hiện bảo trì tiếp theo.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance', 'viin_maintenance_preventive_mode'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/maintenance_equipment_views.xml',

    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
