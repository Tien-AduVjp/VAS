{
    'name': 'Geo Routes Management',
    'name_vi_VN': 'Quản Lý Tuyến Đường',
    'category': 'Operations/Geographical Routes',
    'summary': 'Geo routes design & management',
    'summary_vi_VN': 'Thiết kế và quản lý tuyến đường',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'version': '1.0.0',
    'description': """
What is does
============
This modules allows users to build geo-routes from combination of partner addresses (res.partner)

Value & Benefit
===============
1. Manage unlimited routes with much and details information for each and every route (e.g. distance, average speed, waypoints in routes, etc)
2. Inheritance from the existing model res.partner for addressing to shorten learning curves
3. Ready for any routing application development (map integration, logistics, transportation, etc)

Key Features
------------
* Route design & building by combining waypoints
* Each waypoint is link to an address (res.partner model)
* Route sections is automatically computed and created combining two addresses of two consecutive waypoints in the route
* Users can set distance and max moving speed for each and every section
* Estimated Moving time through a section is computed base on the distance and the max moving speed of the section
* Built for other extensions:

    * sales delivery routes preparation
    * fleet operation tracking
    * transportation pricing
    * automatic distance calculation is possible maybe when integrated with base_geolocalize module
    * etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

        """,
    'description_vi_VN': """
Module này làm gì
=================
Mô-đun này cho phép người dùng xây dựng tuyến đường bằng cách kết hợp với địa chỉ của đối tác (res.partner)

Giá trị và Lợi ích
==================
1. Quản lý không giới hạn các tuyến đường với nhiều thông tin chi tiết cho mỗi/mọi tuyến đường (ví dụ, khoảng cách, tốc độ trung bình, địa điểm trong tuyến đường, v.v.)
2. Kế thừa tô mô hình res.partner hiện có để rút ngắn thời gian học tập
3. Sẵn sàng cho bất kỳ ứng dụng phát triển về tuyến đường (tích hợp bản đồ, logistics, vận chuyển, v.v.)

Tính năng chính
---------------
* Thiết kế và xây dựng tuyến đường bằng cách kết hợp các địa điểm
* Mỗi địa điểm liên kết với một địa chỉ (res.partner model)
* Các chặng trong tuyến được tự động tính toán và tạo bằng cách kết hợp địa chỉ của hai địa điểm liên tiếp trong tuyến đường
* Người dùng có thể thiết lập khoảng cách và tốc độ di chuyển tối đa của mỗi/mọi chặng trong tuyến đường
* Tự động tính toán thời gian di chuyển qua một chặng dựa trên khoảng cách và tốc độ di chuyển tối đa của chặng đó
* Các tính năng mở rộng có thể được xây dựng:

    * chuẩn bị tuyến đường giao hàng
    * theo dõi hoạt động đội phương tiện
    * định giá vận chuyển
    * có thể tính toán khoảng cách tự động khi được tích hợp với mô-đun base_geolocalize
    * v.v.

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,
    'depends': ['mail', 'to_base'],
    'data': [
        'data/sequence_data.xml',
        'security/geo_routes_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/route_views.xml',
        'views/route_section_views.xml',
        'views/route_section_line_views.xml',
        'views/waypoint_area_views.xml',
        'views/waypoint_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
