# -*- coding: utf-8 -*-
{
    'name': 'Stock Age Report',
    'name_vi_VN': 'Báo Cáo Tuổi Tồn Kho',
    'version': '0.1.0',
    'category': 'Hidden',
    'summary': 'Stock Age of products by intervals',
    'summary_vi_VN': 'Báo cáo Tuổi tồn kho của sản phẩm theo chu kỳ',
    'description': """
What it does
============

* Stock Age is the amount of time the goods stay in the enterprise's warehouse. The stock age always starts with the receiving date to the present.
* For inventory management, goods with great stock age causes problems such as:

   * Enterprises have stagnation of capital in the warehouse
   * More costs for inventory management and preservation
   * Risk of loss due to old-aged stocks being reduced in price

* This module adds ```Stock Age Report``` in the Inventory application, allowing users to track the stock age of products by intervals, upto any date. 

Key Features
============

* Allows user to define the period length (in days) and number of periods of stock age
* Shows Stock Age of products by intervals
* Track stock age, quantity on hand and valuation of each product/ product category in specific warehouse/location or in all warehouses

Known Issues
============
Currently, Stock Age Report does not support products using the Standard Cost Method.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====

* Tuổi tồn kho là thời gian hàng hóa nằm trong kho của doanh nghiệp, tính từ thời điểm hàng được nhập vào kho tới hiện tại. 
* Đối với công việc quản lý tồn kho, việc hàng hóa có tuổi tồn kho lớn gây ra các vấn đề như: 

   * Doanh nghiệp bị ứ đọng vốn trong kho 
   * Tốn thêm nhiều chi phí cho việc quản lý, bảo quản hàng tồn kho 
   * Nguy cơ tổn thất do hàng hóa để lâu bị giảm giá

* Mô-đun này tạo thêm mục ```Báo cáo Tuổi tồn kho``` trong ứng dụng Kho vận, giúp người dùng theo dõi tuổi tồn kho của sản phẩm tính đến ngày bất kỳ. 

Tính năng nổi bật
=================

* Cho phép người dùng định nghĩa độ dài chu kỳ tồn kho của sản phẩm (theo ngày) và số lượng chu kỳ theo dõi 
* Theo dõi thời gian tồn kho và giá của sản phẩm ở từng kho/ địa điểm cụ thể hoặc trên tất cả các kho
* Báo cáo Tuổi tồn kho của sản phẩm theo chu kỳ

Vấn đề còn tồn đọng
===================
Hiện tại, Báo cáo tuổi kho chưa hỗ trợ các sản phẩm sử dụng Phương pháp giá vốn Tiêu chuẩn.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': ['stock_account', 'to_location_warehouse', 'to_base'],
    'data': [
        'data/asset.xml',
        'data/main_template.xml',
        'views/search_template_view.xml',
        'views/menu_action.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'qweb': [
        'static/src/xml/stock_report_template.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
