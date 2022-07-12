# -*- coding: utf-8 -*-
{
    'name': 'Fleet Stock Picking / Transfer',
    'name_vi_VN': "Giao / Nhận hàng cho Đội phương tiện",
    'category': 'Warehouse',
    'summary': 'Stock Picking and Transfer with Fleet',
    'summary_vi_VN': 'Stock Picking and Transfer with Fleet',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'version': '1.0.4',
    'description': """
What it does
============

Modules *Stock Picking with Fleet* integrate modules of geo routes, stock, stock picking waves, fleet operation planning to not only better support logistics operations
of goods receipts and delivery but also gives more convenient to fleet operators

Key Features
============
* Assign multiple stock transfers (pickings/deliveries) to a vehicle trip for managing your transfers with your fleets
* Plan trips and assign them to your drivers and trip assistants with simple workflows:

    * Draft -> Confirmed -> In Operation -> Done
    * Draft -> Confirmed -> Cancelled
    * Draft -> Confirmed -> Cancelled -> Draft

* Adding vehicle cost during trip operation
* Trip Operator can Validate transfers during the trip upon the transfers are done.
* Auto Computation of Stowage Volume and Weight for all transfers
* Rais Warning / Blocking messages when total Stowage Volume / Weight exceed the vehicle's Warning / Max Volume / Weight
* Print Trip Report that consolidate all the transfer of the trip so that it can be delivered to the driver of the trip as trip instructions
* Manage Drivers and their licenses
* Get insights of drivers' trips
* Integrated with HR for payroll calculation
* Much more feature descriptions could be found on the dependency pages:

    * Geo-Routes Management and Analysis
    * Product Dimensions
    * Fleet Load Params
    * Trip Planning
    * Etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

        """,
    'description_vi_VN': """
Chọn Đội Xe Vận Chuyển và Chuyển Dịch Kho
=========================================

Mô-đun *Chọn Đội Xe Vận Chuyển và Chuyển Dịch Kho* này tích hợp các mô-đun Quản lý Tuyến đường, Kho, Hoạch định Hoạt động Đội phương tiện để không chỉ hỗ trợ
tốt hơn cho hoạt động hậu cần của giao và nhận hàng hóa mà còn thuận tiện hơn cho các nhà khai thác phương tiện

Tính năng nổi bật
=================
* Chỉ định nhiều dịch chuyển kho (giao / nhận) cho chuyến đi để quản lý dịch chuyển với đội phương tiện của bạn
* Lập kế hoạch chuyến đi và chỉ định chúng cho lái chính và lái phụ của chuyến đi với quy trình đơn giản:

    * Dự thảo -> Xác nhận -> Đang hoạt động -> Xong
    * Dự thảo -> Xác nhận -> Đã hủy
    * Dự thảo -> Xác nhận -> Đã hủy -> Dự thảo

* Thêm chi phí phương tiện trong quá trình hoạt động của chuyến đi
* Người dùng thuộc nhóm quyền Người Khai thác của ứng dụng Hoạch định Hoạt động Đội phương tiện có thể Xác nhận dịch chuyển trong suốt chuyến đi khi dịch chuyển được thực hiện.
* Tự động tính toán khối lượng và dung tích xếp dỡ cho tất cả các dịch chuyển
* Hiển thị thông điệp Cảnh báo / Chặn khi Dung tích Xếp dỡ / Trọng lượng vượt quá Cảnh báo / Dung tích tối đa / Trọng lượng của xe
* In Báo cáo chuyến đi hợp nhất tất cả dịch chuyển của chuyến đi để có thể gửi cho lái xe của chuyến đi theo lộ trình chuyến đi
* Quản lý lái xe và giấy phép của họ
* Nhận thông tin chi tiết về các chuyến đi của lái xe
* Tích hợp với Nhân sự để tính lương
* Có thể tìm thấy nhiều mô tả tính năng hơn trên các trang phụ thuộc:

    * Quản lý Tuyến đường
    * Kích thước Sản phẩm
    * Thông Số Tải Trọng Của Phương Tiện
    * Lập kế hoạch Chuyến đi
    * Vân vân

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise


        """,
    'depends': ['stock', 'to_fleet_load_params', 'to_product_dimensions', 'to_fleet_operation_planning',
                'viin_remove_only_reference_from_one2many'],
    'data': [
#         'data/res_config_settings.xml',
        'security/ir.model.access.csv',
        'wizards/add_stock_picking_views.xml',
        'views/stock_picking_view.xml',
        'views/fleet_vehicle_trip_views.xml',
        'views/trip_print_report.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
