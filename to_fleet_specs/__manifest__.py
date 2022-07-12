{
    'name': "Fleet Specifications",
    'name_vi_VN': 'Thông số Kỹ Thuật Đội phương Tiện',
    'summary': """
Additional fields for vehicle parameters""",
    'summary_vi_VN': """
Bổ sung thêm các trường là thông số của phương tiện""",
    'description': """
Key Features
============
* Vehicle Class: manage unlimited vehicle classes. For example: Trucks 2~4 Tons, Trucks 4~10 Tons, Bus 29 Seats, etc
* Vehicle Type: a selection field with options: Car, Truck, Bus for Vehicle type to categorize your fleet in such the types
* Year Made: the year in which the vehicle was made
* Self Weight: the self weight of the vehicle in kilograms
* Engine Serial Number: the serial of the vehicle engine
* Trailer Inner Height: The inner height in meters of the built-in trailer. This applies to vehicles in type of Truck only.
* Trailer Inner Width: The inner width in meters of the built-in trailer. This applies to vehicles in type of Truck only.
* Trailer Inner Length: The inner length in meters of the built-in trailer. This applies to vehicles in type of Truck only.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính
===============
* Phân cấp Phương tiện: quản lý phân cấp phương tiện không giới hạn. Ví dụ: Xe tải 2~4 tấn, Xe tải 4~10 tấn, Xe buýt 29 chỗ, v.v.
* Kiểu Phương tiện: danh sách các tùy chọn: Ô tô, Xe tải, Xe buýt cho kiểu phương tiện để phân loại đội phương tiện của bạn theo các kiểu như vậy
* Năm sản xuất: năm mà phương tiện được sản xuất
* Tự trọng: tự trọng của phương tiện tính bằng kilo-gam
* Số máy: số máy của phương tiện
* Chiều cao bên trong thùng hàng: Chiều cao bên trong tính bằng mét của thùng hàng tích hợp. Điều này chỉ áp dụng cho các kiểu xe trong kiểu Xe tải.
* Chiều rộng bên trong thùng hàng: Chiều rộng bên trong tính bằng mét của thùng hàng tích hợp. Điều này chỉ áp dụng cho các kiểu xe trong kiểu Xe tải.
* Chiều dài bên trong thùng hàng: Chiều dài bên trong tính bằng mét của thùng hàng tích hợp. Điều này chỉ áp dụng cho các kiểu xe trong kiểu Xe tải.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Fleet',
    'version': '1.1.0',
    # any module necessary for this one to work correctly
    'depends': ['fleet'],

    # always loaded
    'data': [
        'data/vehicle_type_data.xml',
        'data/vehicle_class_data.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_view.xml',
        'views/vehicle_class_view.xml',
        'views/vehicle_type_view.xml',
    ],

    'demo': ['demo/fleet_demo.xml'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
