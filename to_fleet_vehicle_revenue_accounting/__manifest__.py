# -*- coding: utf-8 -*-
{
    'name': "Fleet Revenue Accounting",
    'name_vi_VN': 'Kế Toán Doanh Thu Đội Phương Tiện',
    'summary': """
Integrate Fleet Vehicle Revenue Modeling and Fleet Accounting""",
    'summary_vi_VN': """
Tích hợp mô-đun Mô Hình Hóa Doanh Thu Của Đội Phương Tiện và Kế Toán Đội Phương Tiện""",
    'description': """
What it does
============
This module provides integration between the Fleet Accounting application and Fleet Vehicle Revenue Modeling to allow record and invoice your customer for services related to your fleet

Key Features
============
1. Fleet Users record revenue made from vehicles in the Fleet Management application
2. Accountants generate customer invoices from such the vehicle revenue records
3. Accountant record customer invoices and allocated the invoice amounts across the vehicles of the fleet
4. Vehicle revenue Analysis

    * Analysis revenue By

        * Vehicle
        * Vehicle service type
        * Vehicle revenue type (Contract, Service)
        * Date of revenue (Date / Week / Month / Quarter / Year)
        * Invoice
        * Customer
        * Status (which is either Not Invoiced | Invoiced but Not Paid | Invoiced and Paid)
        * Company (for multi-company environment support)

    * Measure

        * Revenue Amount
        * Revenue Count (number of records)

    * Report types:

        * Pivot
        * Graph

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Mô-đun này cung cấp tích hợp giữa mô-đun Mô Hình Hóa Doanh Thu Của Đội Phương Tiện và Kế Toán Đội Phương Tiện để cho phép ghi lại và lập hóa đơn cho khách hàng của bạn cho các dịch vụ liên quan đến đội phương tiện của bạn.

Tính năng chính
===============
1. Đội phương tiện người dùng ghi lại doanh thu từ các phương tiện trong ứng dụng Quản Lý Đội Phương Tiện
2. Kế toán tạo hóa đơn khách hàng từ bản ghi doanh thu phương tiện
3. Kế toán ghi hóa đơn của khách hàng và phân bổ số tiền hóa đơn vào các xe của đội phương tiện
4. Phân tích doanh thu xe

    * Phân tích doanh thu theo

        * Phương tiện
        * Kiểu dịch vụ phương tiện
        * Kiểu doanh thu phương tiện (Hợp đồng, Dịch vụ)
        * Ngày doanh thu (Ngày / Tuần / Tháng / Quý / Năm)
        * Hóa đơn
        * Khách hàng
        * Trạng thái (Chưa được lập hóa đơn | Hóa đơn nhưng chưa thanh toán | Hóa đơn và thanh toán)
        * Công ty (để hỗ trợ cho môi trường nhiều công ty)

    * Đo lường

        * Số tiền doanh thu
        * Tổng doanh thu (số lượng của bản ghi)

    * Kiểu thông báo:

        * Trục
        * Đồ thị

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_vehicle_revenue', 'to_fleet_accounting'],

    # always loaded
    'data': [
        'data/cron_data.xml',
        'security/ir.model.access.csv',
        'security/fleet_security.xml',
        'views/to_fleet_vehicle_revenue_accounting_templates.xml',
        'views/fleet_vehicle_revenue_views.xml',
        'views/account_move_line_views.xml',
        'views/account_analytic_line_views.xml',
        'wizard/fleet_vehicle_revenue_invoicing_wizard_views.xml',
        'wizard/vehicle_revenue_allocation_wizard_views.xml',
        'views/account_move_views.xml',
        'views/fleet_vehicle_revenue_report.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'application': False,
    'auto_install': False,   #  Set is True after upgrade for Odoo 14
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
