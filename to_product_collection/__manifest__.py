{
    'name': "Product Collection",
    'name_vi_VN': "Bộ sưu tập Sản phẩm",

    'summary': """
Add collection to Products""",
    'summary_vi_VN': """
Phân loại Sản Phẩm theo Bộ sưu tập""",

    'description': """
Key Features
============
* This application allows you to categorize your product by Collections.
* A collection consists of the following information:

1. Name: The name of the collection, which is unique and translatable for multilingual support
2. Product Templates: list of all product templates that belong to this collection
3. Products: list of all products that belong to this collection. Shown if Product Variants feature is activated
4. Description: the description of the collection which also supports multilingual

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
* Mô-đun này cho phép phân loại Sản phẩm theo Bộ sưu tập.
* Một Bộ sưu tập bao gồm các thông tin sau:

1. Tên: Tên của Bộ sưu tập, phải là duy nhất và hỗ trợ đa dịch ngôn ngữ
2. Mẫu Sản phẩm: danh sách tất cả các mẫu Sản phẩm thuộc Bộ sưu tập
3. Sản phẩm: danh sách tất cả các Sản phẩm thuộc Bộ sưu tập. Hiển thị nếu tính năng Biến thể Sản phẩm được kích hoạt
4. Mô tả: Mô tả về Bộ sưu tập, hỗ trợ dịch đa ngôn ngữ

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
        'views/product_collection_views.xml',
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
