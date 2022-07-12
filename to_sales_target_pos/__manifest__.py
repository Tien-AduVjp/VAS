# -*- coding: utf-8 -*-
{
    'name': "Sales Target Management - Point of Sales",
    'name_vi_VN': "Quản lý mục tiêu doanh số - Điểm bán lẻ",
    'summary': """
Sales Targets for Point of Sales""",
    'summary_vi_VN': """
Mục tiêu doanh số cho điểm bán lẻ""",
    'description': """
What it does
============
This module integrates the Sales Target Management (to_sales_target) and Point of Sales (point_of_sale) application
to allow you to manage sales targets for sales persons and sales team in the Point of Sales application

Key Features
============
#. Assign a Sales Team for a Point of Sale
#. Manage Sales Targets for salespersons in Point of Sales

   * Salespersons submit their target
   * Sales Team Leader approves/refuses/adjusts the target

#. Manage Sales Targets for Points of Sales

   * Team Leader register their team's sales target
   * Regional Sales Manager can either approve or refuse and request changes

#. Measure sales targets in reach automatically

   * With Individuals / Salespersons

     * For Point of Sales

       * Total sales amount recorded in Point of Sales application without an issued invoice 
       * Total invoiced sales amount recorded in Point of Sales application 
       * Total sales amount recorded in Point of Sales application, including invoiced and uninvoiced sales
       * Target Reached (in percentage (%), based on the Point of Sales Sales data

     * For All Channels

       * Sales Total from all channels. *E.g. Sales, PoS, Website*
       * Target Reached (in percentage (%))

   * With A Sales Team

     * For Point of Sales

       * Total sales amount recorded in Point of Sales application without an issued invoice 
       * Total invoiced sales amount recorded in Point of Sales application 
       * Total sales amount recorded in Point of Sales application, including invoiced and uninvoiced sales
       * Target Reached (in percentage (%), based on the Point of Sales Sales data)

     * For All Channels

       * Sales Total from all channels. *E.g. Sales, PoS, Website*
       * Target Reached (in percentage (%))

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này tích hợp ứng dụng Quản lý mục tiêu doanh số (to_sales_target) và Điểm Bán Lẻ (point_of_sale) để cho phép bạn quản
lý mục tiêu doanh số cho nhân viên kinh doanh và đội bán hàng trong ứng dụng Điểm bán lẻ

Tính năng nổi bật
=================
#. Chỉ định một đội bán hàng cho điểm bán lẻ
#. Quản lý mục tiêu doanh số cho nhân viên bán hàng tại ứng dụng Điểm bán lẻ

   * Nhân viên bán hàng đề xuất mục tiêu doanh số của họ
   * Đội trưởng bán hàng có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số do nhân viên đề xuất

#. Quản lý mục tiêu doanh số cho Điểm bán lẻ

   * Đội trưởng đăng ký mục tiêu doanh số của đội mình
   * Quản lý bán hàng khu vực có quyền phê duyệt/điều chỉnh/từ chối mục tiêu doanh số

#. Đo lường mục tiêu bán hàng tự động

   * Dành cho cá nhân/nhân viên kinh doanh

     * Đối với điểm bán lẻ

       * Tổng doanh thu bán hàng của Điểm Bán Lẻ mà không xuất hóa đơn
       * Tổng doanh thu bán hàng của Điểm Bán Lẻ mà đã được xuất hóa đơn
       * Tổng doanh thu ở Điểm bán lẻ, bao gồm cả doanh thu xuất hóa đơn và không xuất hóa đơn
       * Mục tiêu đã đạt (tính theo phần trăm (%), dựa theo dữ liệu của Điểm bán lẻ)

     * Đối với tất cả các kênh

       * Tổng doanh số từ tất cả các kênh. *VD: Bán Hàng, Điểm bán lẻ, Website,...*  
       * Mục tiêu đã đạt (tính theo phần trăm (%))

   * Dành cho đội bán hàng

     * Đối với điểm bán lẻ

       * Tổng doanh thu bán hàng của Điểm Bán Lẻ mà không xuất hóa đơn
       * Tổng doanh thu bán hàng của Điểm Bán Lẻ mà đã được xuất hóa đơn
       * Tổng doanh thu ở Điểm bán lẻ, bao gồm cả doanh thu xuất hóa đơn và không xuất hóa đơn
       * Mục tiêu đã đạt (tính theo phần trăm (%), dựa theo dữ liệu của Điểm bán lẻ)

     * Đối với tất cả các kênh 

       * Tổng doanh số từ tất cả các kênh. *VD: Bán Hàng, Điểm bán lẻ, Website*
       * Mục tiêu đã đạt (tính theo phần trăm (%))
 
Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_sales_target_sale', 'pos_sale'],

    # always loaded
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/pos_order_views.xml',
        'views/personal_sales_target_views.xml',
        'views/team_sales_target_views.xml',
        'views/report_pos_order_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
