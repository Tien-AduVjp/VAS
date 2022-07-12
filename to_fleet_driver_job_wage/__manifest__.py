{
    'name': "Driver Job Wage",
    'name_vi_VN': "Lương Khoán Lái Xe",
    'summary': """
Calculate Driver's wage on job/trip basis
        """,
    'summary_vi_VN': """
Tính toán lương cho lái xe dựa trên cơ sở lương khoán / chuyến đi
        """,
    'description': """
What is does
============
This application and its dependencies extends Odoo's functionality to allow to calculate fleet drivers wage on trips basis

Master Data
-----------

1. Job Wage Definition

    Each job wage definition consists of the following information
    
    * Route: the geo-route applied
    * Vehicle: the vehicle applied
    * Allowance: the amount credited to the driver for each trip of the route and vehicle mentioned above
    * Fleet Service Type: the service type for Fleet cost integration.

2. Fleet Fuel Price

    To log fuel price history which consists of the following information
    
    * Price
    * Date: the date from which the price comes into effective

Payroll Integration
-------------------

1. Open a new payslip
2. Specify employee and payslip period
3. Odoo will count number of trips that have been done by the corresponding driver
4. Issue job wage calculation based on the definitions of Job Wage and number of done trips


Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Module này làm gì
=================
Ứng dụng này và các phụ thuộc của nó mở rộng chức năng của Odoo để cho phép tính toán lương cho lái xe dựa trên cơ sở các chuyến đi

Dữ liệu gốc
-----------

1. Định mức Lương khoán

     Mỗi định mức lương khoán bao gồm các thông tin sau
    
     * Tuyến đường: tuyến đường được áp dụng
     * Phương tiện: phương tiện được áp dụng
     * Phụ cấp: số tiền phụ cấp của lái xe cho mỗi chuyến đi của tuyến đường và phương tiện nêu trên
     * Kiểu Dịch vụ Phương tiện: kiểu dịch vụ để tổng hợp chi phí phương tiện.

2. Giá nhiên liệu cho Phương tiện

     Để ghi lại lịch sử giá nhiên liệu bao gồm các thông tin sau
    
     * Giá bán
     * Ngày: ngày giá có hiệu lực

Tích hợp bảng lương
-------------------

1. Mở phiếu lương mới
2. Chỉ định thời hạn của nhân viên và phiếu lương
3. Odoo sẽ tính số chuyến đã được lái xe tương ứng thực hiện
4. Đưa ra cách tính lương khoán dựa trên định mức lương khoán và số lượng chuyến đã thực hiện


Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Fleet',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_fleet_operation_planning', 'to_hr_payroll', 'account'],

    # always loaded
    'data': [
        'data/fleet_service_type_data.xml',
        'security/ir.model.access.csv',
        'views/fleet_fuel_price_views.xml',
        'views/fleet_job_wage_definition_views.xml',
        'views/fleet_vehicle_trip_views.xml',
        'views/hr_payslip_views.xml',
        'views/report_payslip_template_views.xml',
        'views/report_payslipdetails_template_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
