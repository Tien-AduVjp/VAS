{
    'name': "Stock Equipment Maintenance Schedule",
    'name_vi_VN': "Lịch Bảo Trì Thiết Bị Kho",
    'summary': """
Add maintenance schedule information from product to related equipment""",
    'summary_vi_VN': """
Thêm thông tin lịch bảo trì từ sản phẩm vào thiết bị liên quan
    """,
    'description': """
What it does
============
This module will add maintenance schedule information from product to new equipments generated automatically from a stock-in transfer

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này sẽ thêm thông tin lịch bảo trì từ sản phẩm sang thiết bị mới (được tạo tự động từ dịch chuyển kho)

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['to_product_maintenance_schedule', 'to_stock_equipment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_equipment_views.xml',
        'views/stock_production_lot_views.xml',
        'views/maintenance_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
