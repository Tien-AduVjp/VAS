# -*- coding: utf-8 -*-
{
    'name': "Fleet Accounting",
    'name_vi_VN': "Kế Toán Đội Phương Tiện",

    'summary': """
Integrate Fleet with Accounting""",
    'summary_vi_VN': 'Tích hợp mô-đun Đội phương tiện và mô-đun Kế Toán',
    'description': """
Integrate Fleet application with Accounting application

Key Features
============
1. Associate Fleet Service Type with a Product for invoicing purpose
2. Associate an invoice line with vehicle costs for cost distribution to vehicles
3. Associate accounting journal item with vehicles
4. Associate accounting analytics journal item with vehicles
5. Create vendor bills (supplier invoices) from vehicle costs
6. Create vendor bills from vehicle service logs
7. Create vendor bills from vehicle fuel logs
8. Distribute/Allocate vender bills amount to vehicle costs
9. New Vehicle cost report to allow analyse costs distributed to vehicles

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    
    'description_vi_VN':"""
Tích hợp ứng dụng 'Đội phương tiện' và ứng dụng 'Kế Toán' 

Tính năng nổi bật
=================
1. Liên kết Kiểu Dịch vụ của Đội phương tiện với một Sản phẩm để xuất hóa đơn cho chi phí phương tiện.
2. Phân bổ chi phí phương tiện trên từng dòng hóa đơn
3. Gắn Phương tiện với Phát sinh kế toán
4. Gắn Phương tiện với Phát sinh Kế toán quản trị
5. Xuất hóa đơn Nhà cung cấp từ Chi phí phương tiện
6. Xuất hóa đơn Nhà cung cấp từ Nhật ký Dịch vụ phương tiện
7. Xuất hóa đơn Nhà cung cấp từ Nhật ký Đổ nhiên liệu
8. Phân bổ số tiền trên hóa đơn nhà cung cấp cho chi phí phương tiện
9. Báo cáo chi phí phương tiện, cho phép phân tích chi phí phân bổ cho Đội phương tiện

Ấn bản được Hỗ trợ
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
    'category': 'Accounting & Finance',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'fleet'],

    # always loaded
    'data': [
        'data/product_category_data.xml',
        'data/account_analytic_data.xml',
        'data/cron_data.xml',
        'security/fleet_security.xml',
        'security/ir.model.access.csv',        
        'views/to_fleet_accounting_templates.xml',
        'views/fleet_service_type_views.xml',
        'views/fleet_vehicle_cost_views.xml',
        'views/fleet_vehicle_log_contract_views.xml',
        'views/fleet_vehicle_log_services_views.xml',
        'views/fleet_vehicle_log_fuel_views.xml',
        'views/account_move_line_views.xml',
        'views/account_move_views.xml',
        'views/account_analytic_line_views.xml',
        'views/fleet_vehicle_cost_report.xml',
        'wizard/fleet_vehicle_cost_invoicing_wizard_views.xml',
        'wizard/fleet_vehicle_log_services_invoicing_wizard_views.xml',
        'wizard/fleet_vehicle_log_fuel_invoicing_wizard_views.xml',
        'wizard/vehicle_cost_allocation_wizard_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 199.8,
    'currency': 'EUR',
    'license': 'OPL-1',
}
