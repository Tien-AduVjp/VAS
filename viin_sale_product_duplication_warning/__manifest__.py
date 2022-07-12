{
    'name': "Sales Order Product Duplication Warning",
    'name_vi_VN': "Cảnh báo trùng Sản phẩm trên Đơn bán",

    'summary': """Show warning on product duplication (appearing more than 1 time) on the same sales order""",

    'summary_vi_VN': """Hiển thị cảnh báo các sản phẩm bị trùng (được chọn nhiều hơn 1 lần) trên cùng một đơn bán""",

    'description': """
What it does
============
This module will:

1. Show warning on product duplication (appearing more than 1 time for the same sales order) on the order form view
2. Provide an additional filter to help users find sales orders/quotations that contain duplicated products
3. Enable/Disable the feature for a specific product by a configurable option on the product form view

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này:

1. Hiển thị cảnh báo trùng lặp sản phẩm cho cùng một đơn bán (được chọn nhiều hơn 1 lần trên cùng đơn bán) trên giao diện form của đơn bán
2. Cung cấp bộ lọc để trợ giúp người dùng tìm kiếm các đơn bán / báo giá mà có chứa các sản phẩm bị trùng lặp
3. Kích hoạt/Vô hiệu tính năng này đối với từng sản phẩm cụ thể, cấu hình được trên giao diện form của sản phẩm.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Productivity',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'to_sale_line_numbering'],

    # always loaded
    'data': [
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
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
