{
    'name': "Warranty Sale Stock",

    'summary': """
Update warranty informations from Sale Order Line to Stock Move Line.        
        """,

    'summary_vi_VN': """
Đưa thông tin bảo hành từ các Dòng đơn hàng bán sang Stock Move Line
    	""",
        
    'description': """
What it does
============
This is a dependency module of to_warranty_sale & to_warranty_stock and will be automatically installed when these 2 modules are installed.

Key Features
============
* Add the Sales Order field on the Warranty Claim to select the sales order containing the product with Lot/Serial number
* When validating stock picking of a sales order with lot/serial number:

    - Bring warranty policies from the Sales Order Line to Stock Move Line.
    - Update warranty start date and sales order informations for Lot/serial number
    
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    
    'description_vi_VN': """
Mô tả
=====
Đây là mô-đun phụ thuộc của to_warranty_sale & to_warranty_stock và sẽ tự động được cài đặt khi 2 mô-đun này được cài đặt.

Tính năng nổi bật
=================
* Thêm trường Đơn hàng bán trên Yêu cầu bảo hành để chọn đơn bán có chứa sản phẩm mang số Lô/sê-ri
* Khi xác nhận giao hàng bán sản phẩm có Lô/sê-ri:

    - Đưa thông tin các chính sách bảo hành từ các dòng đơn hàng bán sang Stock Move Line
    - Cập nhật ngày bắt đầu bảo hành và đơn hàng bán trên Lô/sê-ri
    
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
    'category': 'Warranty Management',
    'version': '0.1',
    'depends': ['to_warranty_stock', 'sale_stock', 'to_warranty_sale'],
    'data': [
        'views/stock_production_lot_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
