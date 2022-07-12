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
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['to_product_maintenance_schedule', 'to_stock_equipment'],

    # always loaded
    'data': [
        'views/equipment_maintenance_schedule_views.xml',
        'security/ir.model.access.csv',
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
