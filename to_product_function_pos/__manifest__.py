{
    'name': "Point of Sales & Product Function",
    'name_vi_VN':"Điểm Bán Lẻ và Chức Năng Sản Phẩm",

    'summary': """Integrate Product Function for Point of Sales""",
    'summary_vi_VN':"""Tích hợp Chức năng Sản phẩm cho Điểm bán lẻ""",

    'description': """
Key Features
============
Extend the application Product Function to get integrated with Point of Sales for analyzing sales of
product function done with Point of Sales application

1. Sales/Revenue by a product function
2. Product Function Sales over the period of time (i.e. Day, Week, Month, Year)
3. Product Function Sales by Salesperson
4. Product Function Sales by Point of Sales
5. Product Function Sales by Point of Sales Session
6. Etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
Mở rộng ứng dụng Chức năng Sản phẩm tích hợp cho Điểm Bán Lẻ để phân tích đơn hàng theo Chức năng Sản phẩm
ở mỗi ứng dụng điểm bán lẻ

1. Đơn hàng/doanh thu theo chức năng sản phẩm
2. Chức năng Sản phẩm theo thời gian (vd. Ngày, Tuần, Tháng, Năm)
3. Chức năng Sản phẩm theo người bán
4. Chức năng Sản phẩm theo điểm bán lẻ
5. Chức năng Sản phẩm theo phiên điểm bán lẻ
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
    'category': 'Point of sale',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'to_product_function'],

    # always loaded
    'data': [
        'views/product_function_pos_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
