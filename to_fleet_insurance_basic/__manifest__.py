# -*- coding: utf-8 -*-
{
    'name': "Fleet Insurance Basic",
    'name_vi_VN': 'Bảo Hiểm Cơ Bản Đội Phương Tiện',
    'summary': """Manage basic insurances for your fleet""",
    'summary_vi_VN': """Quản lý bảo hiểm cơ bản cho đội phương tiện của bạn""",
    'description': """
Key features
============
1. Manage unlimited insurance type for your vehicle

    Each insurance type consists of the following information
    
    * Name: the name of the insurance type. For example, Civil Liability Insurance, Material insurance, etc
    * Default Period: the default period for Insurance of this type, which aims to save input time during insurance document creation
    * Days to notify: the default value of the number of days to notify prior to expiration of insurance of this type
    * Insurances: a list of insurances of this type issued
    * Vehicles: a list of vehicle that have this insurance type
    
2. Insurance

    Is an Odoo document that present insurance for a vehicle in period of time. Each insurance document consists of the following information
    
    * Reference: the reference number of the insurance
    * Vehicle: the vehicle for which the insurance is
    * Type: the type of insurance, which is either of the predefined insurance types
    * Start Date: the date from which the insurance comes into effect
    * Expire Date: the date from which the insurance gets expired
    * Days to notify: the number of days to notify prior to expiration of insurance
    
3. Extendable

    Insurance document was designed with an abstract model that may help ease further extensions. For example, Insurance Management for vehicle trailers, etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN':"""
Tính năng chính
===============
1. Quản lý không giới hạn loại bảo hiểm cho phương tiện của bạn

    Mỗi loại bảo hiểm bao gồm các thông tin sau
    
    * Tên: tên của loại bảo hiểm. Ví dụ, Bảo Hiểm Trách Nhiệm Dân Sự, Bảo Hiểm Vật Chất, v.v.
    * Thời hạn mặc định: thời hạn mặc định cho Bảo hiểm của loại này, nhằm tiết kiệm thời gian nhập thông tin khi tạo tài liệu bảo hiểm
    * Ngày để thông báo: giá trị mặc định của số ngày cần thông báo trước khi hết hạn của bảo hiểm của loại này
    * Bảo hiểm: danh sách các loại bảo hiểm thuộc loại này được phát hành
    * Phương tiện: danh sách các phương tiện có loại bảo hiểm này
    
2. Bảo hiểm

    Là một tài liệu Odoo trình bày bảo hiểm cho một phương tiện trong khoảng thời gian. Mỗi tài liệu bảo hiểm bao gồm các thông tin sau
    
    * Tham chiếu: số tham chiếu của bảo hiểm
    * Phương tiện: phương tiện cho bảo hiểm
    * Kiểu: loại bảo hiểm, là một trong các loại bảo hiểm được xác định trước
    * Ngày bắt đầu: ngày mà bảo hiểm có hiệu lực
    * Ngày hết hạn: ngày mà bảo hiểm hết hạn
    * Ngày để thông báo: số ngày cần thông báo trước khi bảo hiểm hết hạn
    
3. Khả năng mở rộng

    Tài liệu bảo hiểm được thiết kế với một mô hình trừu tượng có thể giúp dễ dàng mở rộng hơn nữa. Ví dụ, Quản lý Bảo hiểm cho xe kéo, v.v.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Fleet Management',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'data/email_template_data.xml',
        'data/insurance_type_data.xml',
        'data/scheduler_data.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/insurance_type_view.xml',
        'views/fleet_vehicle_insurance_view.xml',
        'views/fleet_vehicle_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
