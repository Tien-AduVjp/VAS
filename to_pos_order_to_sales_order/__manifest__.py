{
    'name': "PoS Order to Sales Quotation",
    'name_vi_VN': "Báo giá đơn hàng",
    'summary': """
Convert a PoS Order to a Sales Quotation at PoS screen""",
    'summary_vi_VN': """
Chuyển đổi đơn hàng PoS sang báo giá đơn hàng tại màn hình PoS.""",
    'description': """
What it does
============
This module allows you to convert a PoS Order (in Point of Sales application) to a Sales Quotation (in Sales Management application)
right from PoS screen without switching to Sales Management application

Use Cases
---------
1. Customer wants to get quote instead of buying immediately at your shop/store
2. You sell your goods and services both for individual and business customers
3. Customers want to buy something that is not available in your store. Then you want to transfer the sales to another store

Key features
============
1. Convert PoS Order to Sales Quotation with all the data reserved (e.g. product, quantity, pricelist, unit price, customer, taxes, etc)
2. Transfer the sales to another Store/Warehouse: Choose a different Warehouse/Store during conversion in case you want to transfer
   the sales to another store or delivery the goods from a warehouse other than yours
3. Keep track of all the sales order that came from PoS
4. Sales Report in Sales Management application now includes

    * PoS Session
    * Point of Sales
    * PoS Session Responsible User

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này cho phép bạn chuyển đổi một đơn hàng PoS (trong ứng dụng Point of Sales) sang một báo giá đơn hàng (trong ứng dụng Sales Management)
ngay từ màn hình PoS mà không cần thoát khỏi phiên và chuyển sang ứng dụng Sales Management

Tình huống sử dụng
------------------
1. Khách hàng muốn xem báo giá thay vì mua ngay tại của hàng của bạn.
2. Bạn bán hàng hóa và dịch vụ cho cả khách hàng cá nhân và khách hàng Doanh nghiệp.
3. Khách hàng muốn mua một số sản phẩm không có sẵn ở cửa hàng của bạn. Sau đó, bạn muốn chuyển doanh số sang cửa hàng khác.

Tính năng nổi bật
=================
1. Chuyển đổi đơn hàng PoS thành báo giá với tất cả dữ liệu đã nhận (như: sản phẩm, số lượng, bảng giá, khách hàng, thuế, ...).
2. Chuyển doanh số sang của hàng/kho khác: Trong quá trình chuyển đổi, bạn có thể chọn cửa hàng/kho khác nếu bạn muốn chuyển doanh số sang cửa hàng khác hoặc giao hàng từ cửa hàng/kho khác.
3. Theo dõi tất cả các đơn hàng đến từ PoS.
4. Báo cáo bán hàng trong ứng dụng Quản lý Bán hàng sẽ có thêm các thông tin bao gồm:

    * Phiên PoS
    * Điểm bán hàng
    * Người chịu trách nhiệm phiên PoS

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['pos_sale', 'to_location_warehouse'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/assets.xml',
        'views/sale_order_views.xml',
        'views/pos_session_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': [
        'static/src/xml/Screens/TicketScreen/SaleOrder.xml',
        'static/src/xml/Screens/TicketScreen/TicketScreen.xml'
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
