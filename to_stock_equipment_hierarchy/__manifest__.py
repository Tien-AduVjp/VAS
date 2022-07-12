{
    'name': "Inventory Equipment Maintenance Tracking",
    'name_vi_VN': "Truy vết bảo trì thiết bị",

    'summary': """Track Lot/Serial's related maintenances""",

    'summary_vi_VN': """Truy vết bảo trì thiết bị từ số Lô/Seri""",

    'description': """
What it does
============
* On Production Lot form, show all the maintenance requests of the equipments and its parts

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Trên giao diện Lô - Seri, hiển thị danh sách các yêu cầu bảo trì của thiết bị gắn với số lô - seri này, trong đó có bao gồm
cả các yêu cầu bảo trì của các thiết bị con của nó.


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'http://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Manufacturing/Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_equipment', 'to_equipment_hierarchy'],

    # always loaded
    'data': [
        'views/stock_production_lot_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
