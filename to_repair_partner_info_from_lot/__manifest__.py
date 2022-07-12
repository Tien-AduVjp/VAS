{
    'name': "Repair Partner Info From Lot",
    'name_vi_VN': 'Thông tin đối tác trên đơn sửa chữa',
    'summary': """
Update Repair Order's Customer when select lot/serial number
""",

    'summary_vi_VN': """
Cập nhật khách hàng của đơn sửa chữa khi chọn lô/serial
    	""",
    'description': """
What it does
============
Update Repair Order's Customer when select lot/serial number

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Module này làm gì
=================
Cập nhật khách hàng của đơn sửa chữa khi chọn lô/serial

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
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['repair', 'to_stock_production_lot_partner_infor'],
    'data': [
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
