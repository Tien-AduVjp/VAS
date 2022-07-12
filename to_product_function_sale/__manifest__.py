# -*- coding: utf-8 -*-
{
    'name': "Sales Management & Product Function",
    'name_vi_VN':"Bán Hàng và Chức Năng Sản Phẩm",
    
    'summary': """
Integrate Product Function and Sales""",
    'summary_vi_VN':"""
Tích hợp Chức năng Sản phẩm và hoạt động kinh doanh
    """,

    'description': """
Key Features
============
Extend the application Product Function to get integrated with Sales Management application for analyzing sales
of product functions done with Sales Management application

1. Sales/Revenue by a product function
2. Product Function Sales over the period of time (i.e. Day, Week, Month, Year)
3. Product Function Sales by Salesperson
4. Product Function Sales by Sales Team / Channel
5. Product Function Sales by Warehouse
6. Etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng nổi bật
=================
Mở rộng ứng dụng Chức năng Sản phẩm tích hợp cho ứng dụng Quản lý Bán hàng để thống kê đơn bán hàng theo Chức năng
Sản phẩm ở ứng dụng Quản lý Bán hàng

1. Đơn hàng/doanh thu theo Chức năng Sản phẩm
2. Chức năng Sản phẩm theo thời gian (vd. Ngày, Tuần, Tháng, Năm)
3. Chức năng Sản phẩm theo người bán
4. Chức năng Sản phẩm theo nhóm/kênh bán hàng
5. Chức năng Sản phẩm theo nhà kho
6. v.v

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['sale', 'to_product_function'],
    'data': [
        'views/product_function_sale_views.xml',
           ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
