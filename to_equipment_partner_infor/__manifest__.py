{
    'name': "Equipment Warranty Partner",
    'name_vi_VN': "Bảo hành Thiết bị Đối tác",
    'summary': """
Add Vendor, Customer, Warranty Expiry information to Equipment
""",

    'summary_vi_VN': """
Thêm thông tin Nhà cung cấp, Khách hàng, Ngày hết hạn bảo hành vào Thiết bị.
    	""",
    'description': """
Add Vendor, Customer, Warranty Expiry information to the warranty Equipments

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Thêm thông tin Nhà cung cấp, Khách hàng, Ngày hết hạn bảo hành vào Thiết bị.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Productivity',
    'version': '0.1',
    'depends': ['to_warranty_stock', 'to_stock_equipment', 'to_stock_production_lot_partner_infor'],
    'data': [
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
