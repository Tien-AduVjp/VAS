{
    'name': "Warranty Sale",

    'summary': """
Warranty management for sales
        """,

    'summary_vi_VN': """
Quản lý bảo hành cho bán hàng
    	""",

    'description': """
Key Features
============
* This module depends on to_warranty_management module to apply to the Sales module.
* When confirming the sales order, the warranty policy applied to the product will be automatically included in the order line (policies applicable to Sales only).
* When creating a warranty claim for a predefined sales order, the warranty policy applied to this sales order will be automatically converted to the warranty claim.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Module này được phát triển dựa trên module to_warranty_management để áp dụng cho phân hệ bán hàng.
* Khi xác nhận đơn hàng bán, tự động đưa các chính sách bảo hành áp dụng cho sản phẩm vào dòng đơn hàng (chỉ các chính sách áp dụng cho Bán hàng).
* Khi tạo yêu cầu bảo hành nếu có thông tin về đơn hàng bán, hệ thống sẽ tự động lấy chính sách bảo hành áp dụng cho đơn hàng bán này sang yêu cầu bảo hành.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Warranty Management',
    'version': '0.1',
    'depends': ['to_warranty_management', 'sale'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/warranty_claim_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
