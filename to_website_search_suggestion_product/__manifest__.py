# -*- coding: utf-8 -*-
{
    'name': 'Website Search Suggestion Product',
    'name_vi_VN': 'Gợi ý tìm kiếm sản phẩm trên Website',
    'version': '1.0.1',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Product Search Suggestion for Odoo Websites',
    'summary_vi_VN': 'Hiển thị gợi ý sản phẩm khi tìm trên website',
    'category': 'Hidden',
    'sequence': 11,
    'description': """
What it does
============
Website Search Suggestion Product is an module for Odoo that allows customers to search the products easily without typing all the letters and will display the results in dropdown list of search box on website.

* The dropdown list shows products matching search terms
* Customers can easily navigate to the desired product by the search results.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Module này làm gì
=================
Gợi Ý Tìm Kiếm Sản Phẩm Trên Website là một module cho Odoo để cho phép khách hàng dễ dàng tìm kiếm sản phẩm mà không cần gõ tất cả các chữ cái và sẽ hiển thị kết quả trong danh sách xổ xuống của ô tìm kiếm bên ngoài website.

* Danh sách thả xuống hiển thị sản phẩm đề xuất khớp với từ khóa tìm kiếm
* Khách hàng có thể dễ dàng điều hướng đến sản phẩm mong muốn trong kết quả tìm kiếm.

Ấn bản hỗ trợ
================
1.Ấn bản Community 
2.Ấn bản Enterprise 

""",
    'depends': ['to_website_search_suggestion', 'website_sale'],
    'data': [
        'views/search_products.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
