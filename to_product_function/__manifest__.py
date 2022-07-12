{
    'name': "Product Functions",
    'name_vi_VN': "Chức Năng Sản Phẩm",

    'summary': """
Categorize products by Product Functions""",
    'summary_vi_VN':"""
Phân loại Sản phẩm theo Chức năng""",

    'description': """
Key Features
============
* This application allows you to categorize your product by Functions
* A Product Function consists of the following information:

1. Name: The name of the function, which is unique and translatable for multilingual support
2. Product Templates: list of all product templates that belong to this function
3. Products: list of all products that belong to this function. Shown if Product Variants feature is activated
4. Description: the description of the function which also supports multilingual

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
* Ứng dụng này cho phép bạn phân loại sản phẩm của mình theo chức năng
* Một Chức năng Sản phẩm bao gồm những thông tin sau:

1. Tên: Tên của chức năng, phải là duy nhất và hỗ trợ dịch đa ngôn ngữ
2. Mẫu Sản phẩm: Danh sách tất cả các mẫu sản phẩm thuộc về chức năng này
3. Các Sản phẩm: Danh sách tất cả các sản phẩm thuộc về chức năng này. Hiển thị nếu tính năng Biến thể Sản phẩm được kích hoạt
4. Mô tả: Mô tả về chức năng, hỗ trợ dịch đa ngôn ngữ

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
    'depends': ['product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_function_views.xml',
        'views/product_template_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
