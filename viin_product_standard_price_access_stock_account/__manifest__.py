{
    'name': "Product Standard Price Access - Stock Accounting",
    'name_vi_VN': "Truy Cập Giá Tiêu Chuẩn Sản Phẩm - Kế Toán Kho",

    'summary': """
Hide Standard Price on products with non-accessible users
""",

    'summary_vi_VN': """
Ẩn trường Giá vốn trên sản phẩm với những người dùng không có quyền
""",

    'description': """
Key Features
============
Hide Standard Price on products form view with non-accessible users.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Tính năng chính
===============
Ẩn trường Giá vốn trên giao diện chi tiết sản phẩm với những người dùng không có quyền truy cập.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1.0',
    'depends': ['stock_account', 'to_product_standard_price_access_account'],
    'data': [
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
