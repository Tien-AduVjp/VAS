{
    'name': "Sales & Product Collection",
    'name_vi_VN':"Bán hàng và Bộ sưu tập Sản Phẩm",

    'summary': """
Integrate Product Collection and Sales""",
    'summary_vi_VN':"""
Tích hợp Bộ sưu tập Sản phẩm và Bán hàng
    """,

    'description': """
Key Features
============
Extend the application Product Collection to get integrated with Sales Management application for analyzing sales
of product collections done with Sales Management application

1. Sales/Revenue by a product collection
2. Product Collection Sales over the period of time (i.e. Day, Week, Month, Year)
3. Product Collection Sales by Salesperson
4. Product Collection Sales by Sales Team / Channel
5. Product Collection Sales by Warehouse
6. Etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
Mở rộng chức năng Bộ sưu tập Sản phẩm tích hợp với Quản lý Bán hàng cho việc phân tích bán bộ sưu tập sản phẩm

1. Bán/doanh thu theo bộ sưu tập sản phẩm
2. Thống kê bán bộ sưu tập sản phẩm theo thời gian (Ngày, Tuần, Tháng, Năm)
3. Thống kê bán bộ sưu tập sản phẩm theo Nhân viên bán hàng
4. Thống kê bán bộ sưu tập sản phẩm theo Đội ngũ / Kênh bán hàng
5. Thống kê bán bộ sưu tập sản phẩm theo Kho.
6. v.v

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'to_product_collection'],
    'data': [
        'views/product_collection_sale_views.xml',
           ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
