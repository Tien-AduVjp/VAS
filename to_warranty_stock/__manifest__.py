{
    'name': "Warranty Stock",
    
    'name_vi_VN': 'Kho bảo hành',

    'summary': """
Warranty management with Lot / Series
        """,

    'summary_vi_VN': """
Quản lý bảo hành với Lô/Sê-ri
    	""",

    'description': """
Key Features
============
* This module depends on to_warranty_management module, adding some features related to lot/serial in stock module.
* When creating a new Lot / Series, the warranty policies will be taken from the product of this lot / series.
* When creating a new Warranty Claim, if there is a Lot / series selected, the warranty policies will be taken from this Lot / series.
* Allow users to create warranty claims on the Lot/series form.
* Show warranty claim history on the Lot/Series form.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
* Module này được phát triển dựa trên module to_warranty_management, bổ sung thêm các tính năng về Lô/Sê-ri trong phân hệ kho.
* Khi tạo mới Lô/Sê-ri, đưa các chính sách bảo hành áp dụng cho sản phẩm vào Lô/Sê-ri này.
* Khi tạo Yêu cầu bảo hành, nếu có Lô/sê-ri được chọn, các chính sách bảo hành sẽ được đưa từ Lô/sê-ri này sang.
* Cho phép tạo Yêu cầu bảo hành từ Form của Lô/sê-ri.
* Thống kê lịch sử bảo hành của sản phẩm trên Form Lô/Sê-ri.

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
    'depends': ['to_warranty_management', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/stock_production_lot_views.xml',
        'views/warranty_claim_history_view.xml',
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
