# -*- coding: utf-8 -*-
{
    'name': 'Fleet Planning',
    'name_vi_VN': "Hoạch định Phương tiện",
    'category': 'Fleet Transportation',
    'category_vi_VN': 'Vận chuyển với Đội phương tiện',
    'summary': 'Fleet Operation Planning',
    'summary_vi_VN': 'Hoạch định Hoạt động Đội phương tiện',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'version': '1.0.5',
    'description': """
What it does
============

* Module Fleet Operation Planning allows fleet operators to plan and manage vehicle trips and operations. 
* It also allows recording costs related to vehicle trips

Key Features
============
* Scheduled Start Date of the trip
* Scheduled End Date of the trip which is automatically computed based on the scheduled start date and the estimated time to go through the route
* Actual Start Date of the trip
* Actual End Date of the trip
* Driver Assignment
* Driver Assistants Assignment
* Record costs for each and every vehicle trip in Fleet Vehicle Cost for trip cost analysis
* Send Trip information and instructions to the trip's followers (i.e. The driver, the driver assistants, other contacts available in your system)
* Trips Analysis

    * Analysis by 

        * Geo-Route
        * Trip
        * Driver / Employee
        * Vehicle
        * Start Date
        * End Date
        * Status

    * Measurement

        * Actual Time
        * Actual Distance
        * Fuel Consumption
        * Trip Cost
        * Time deviation between Planned vs. Actual
        * Distance deviation between odometer and route's master data

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

        """,
'description_vi_VN':"""
Mô tả
=====

* Mô-đun Hoạch định Hoạt động Đội phương tiện cho phép các nhà khai thác đội phương tiện lập kế hoạch và quản lý các chuyến đi và hoạt động của phương tiện. 
* Mô-đun này cũng cho phép ghi lại các chi phí liên quan đến các chuyến đi của phương tiện.

Tính năng nổi bật
=================
* Ngày bắt đầu theo lịch trình của chuyến đi
* Ngày kết thúc theo lịch trình của chuyến đi được tính toán tự động dựa trên ngày bắt đầu đã lên lịch và thời gian ước tính để đi qua tuyến đường
* Ngày bắt đầu thực tế của chuyến đi
* Ngày kết thúc thực tế của chuyến đi
* Phân công lái xe
* Phân công trợ lý lái xe
* Ghi lại chi phí cho mỗi chuyến đi của phương tiện trong chi phí Đội phương tiện cho phân tích chi phí chuyến đi
* Gửi thông tin và hướng dẫn chuyến đi cho những người theo dõi chuyến đi (ví dụ: Người lái xe, trợ lý lái xe, những người liên hệ khác có sẵn trong hệ thống của bạn)
* Phân tích chuyến đi

    * Phân tích theo

        * Tuyến đường
        * Chuyến đi
        * Lái xe / nhân viên
        * Xe
        * Ngày bắt đầu
        * Ngày kết thúc
        * Trạng thái

    * Đo lường

        * Thời gian thực tế
        * Khoảng cách thực tế
        * Sự tiêu thụ xăng dầu
        * Chi phí chuyến đi
        * Độ lệch thời gian giữa kế hoạch so với thực tế
        * Độ lệch khoảng cách giữa dữ liệu đo đường và dữ liệu chính của tuyến đường

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

        """,
    'depends': ['to_geo_routes', 'to_fleet_driver'],
    'data': [
        'data/sequence_data.xml',
        'security/fleet_security.xml',
        'security/ir.model.access.csv',
        'views/route_views.xml',
        'views/waypoint_views.xml',
        'wizard/vehicle_trip_start_wizard_views.xml',
        'wizard/vehicle_trip_end_wizard_views.xml',
        'wizard/vehicle_trip_register_cost_wizard_views.xml',
        'wizard/wizard_generate_routes_views.xml',
#         'views/fleet_report.xml', We should implement this printed report later
        'views/fleet_vehicle_cost_views.xml',
        'views/fleet_vehicle_trip_views.xml',
        'views/fleet_vehicle_views.xml',
        'views/hr_employee_views.xml',
        'views/res_partner_views.xml',
#         'views/report_fleetoperationplanning.xml',
        'views/fleet_vehicle_odometer_views.xml',
        'views/trip_analysis.xml',
        'views/trip_print_report.xml',
        'data/mail_template_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
