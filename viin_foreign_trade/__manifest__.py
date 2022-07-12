# -*- coding: utf-8 -*-

{
    'name' : 'Foreign Trade, Logistics',
    'old_technical_name': 'to_foreign_trade',
    'name_vi_VN': 'Xuất nhập khẩu',

    'summary': 'Foreign Trade & Logistics Management',
    'summary_vi_VN': 'Quản Lý Ngoại Thương & Logistics',

    'description':"""
Key Features
============
* Flexible logistics route for importing / exporting goods

  * Foreign Purchase Route:

    * Receive in one-step: Vendor location -> Import - Custom Zone -> Stock
    * Receive in two-steps: Vendor location -> Import - Custom Zone -> Input -> Stock
    * Receive in three-steps: Vendor location -> Import - Custom Zone -> Input -> Quality Control -> Stock

  * Foreign Sale Route:

    * Ship Only: Stock -> Export - Custom Zone -> Foreign Customer
    * Pick + Ship: Stock -> Output -> Export - Custom Zone -> Foreign Customer
    * Pick + Pack + Ship: Stock -> Packing Zone -> Output -> Export - Custom Zone -> Foreign Customer

* Stop the picking/deliver at the Custom Zone for custom declaration
* Automatic calculate taxes during custom declaration
* Integrated with Accounting for importing/exporting taxes automatic encoding into accounting system
* Pay importing/exporting taxes

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
* Linh hoạt quá trình nhập / xuất hàng

  * Quá trình mua hàng:

    * Nhận 1 bước: Vị trí nhà cung cấp -> Nhập - Khu vực Thông quan -> Kho
    * Nhận 2 bước: Vị trí nhà cung cấp -> Nhập - Khu vực Thông quan -> Đầu vào -> Kho
    * Nhận 3 bước: Vị trí nhà cung cấp -> Nhập - Khu vực Thông quan -> Đầu vào -> Kiểm soát chất lượng -> Kho

  * Quá trình bán hàng:

    * Chỉ giao hàng: Kho -> Xuất - Khu vực Thông quan -> Khách hàng ngoại thương
    * Lựa chọn + Giao hàng: Kho -> Đầu ra -> Xuất - Khu vực Thông quan -> Khách hàng ngoại thương
    * Lựa chọn + Đóng gói + Giao hàng: Kho -> Vùng đóng gói -> Đầu ra -> Xuất - Khu vực Thông quan -> Khách hàng ngoại thương

* Dừng quá trình lựa chọn/phân phối tại tờ khai khu vực thông quan
* Tự động tính toán thuế trong khu vực thông quan
* Tích hợp với kế toán cho nhập/xuất thuế tự động mã hóa vào hệ thống kế toán
* Thanh toán thuế nhập/xuất

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'version': '1.0.2',
    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Operations/Foreign Trade',
    'sequence': 24,

    'depends': ['sale_stock', 'purchase_stock', 'stock_account', 'to_vat_counterpart', 'to_currency_rate', 'stock_landed_costs'],
    'data': [
        'data/res_company_data.xml',
        'data/stock_data.xml',
        'data/update_partners.xml',
        'data/update_purchase_orders.xml',
        'data/update_sale_orders.xml',
        'data/product_data.xml',
        'security/foreign_trade_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'wizard/custom_dec_payment_view.xml',
        'views/stock_landed_cost_views.xml',
        'views/custom_declaration_import_views.xml',
        'views/custom_declaration_export_views.xml',
        'views/product_views.xml',
        'views/stock_location_views.xml',
        'views/stock_views.xml',
        'views/stock_picking_type_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_views.xml',
        'views/sale_views.xml',
        'views/account_views.xml',
        'views/res_config_settings_views.xml',
        'views/warehouse_views.xml',
        'views/account_tax_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
