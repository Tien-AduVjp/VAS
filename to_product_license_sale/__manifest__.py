# -*- coding: utf-8 -*-
{
    'name': "Product Licenses - Sales",
    'name_vi_VN':"Giấy Phép Sản Phẩm - Bán Hàng",

    'summary': """
Sell products with licensing""",
    'summary_vi_VN':"""
Bán Sản phẩm với Giấy phép""",

    'description': """
This module integrates the application Sales and the application Product Licenses Management to allow selling products with license indicators

Key Features
============

1. Select a product on a sale order line will automatically load the product's license(s) into the sales order line.
2. Inject license information into the sales description column on the sales/quotation PDF report
3. Include related license contents in the PDF version of the quotation / sales order automatically when the products sold are licensed
4. View related license(s) on the quotation/sale order form with one click
5. Statistic on Number of sales per license and license version

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này tích hợp ứng dụng Bán hàng và ứng dụng Quản lý Giấy phép Sản phẩm cho phép bán sản phẩm với giấy phép

Tính năng chính
============

1. Chọn một sản phẩm trên một dòng đơn bán hàng sẽ tự động tải giấy phép của sản phẩm vào trong dòng đơn bán hàng. Người bán hàng có thể quyết định giữ một hoặc nhiều giấy phép trước khi xác nhận đơn hàng
2. Thêm thông tin giấy phép vào cột mô tả đơn hàng của bản báo cáo PDF đơn hàng/báo giá
3. Tự động thêm thông tin liên quan đến giấy phép vào bản báo cáo PDF báo giá/đơn hàng khi sản phẩm được đã bán đã được cấp phép
4. Hiển thị thông tin liên quan đến giấy phép sản phẩm chỉ với một click
5. Thống kê số lượng bán trên mỗi giấy phép và phiên bản giấy phép

Ấn bản hỗ trợ
==================
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author' : "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'support': 'apps.support@viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_product_license', 'sale'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
        'views/product_license_views.xml',
        'views/product_license_version_views.xml',
        'views/sale_order_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
