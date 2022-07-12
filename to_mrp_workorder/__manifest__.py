{
    'name': 'Mrp Workorder',
    'old_technical_name': 'mrp_workorder',
    'version': '1.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Manufacturing',
    'sequence': 51,
    'summary': """Work Orders, Planing, Stock Reports.""",
    'depends': ['mrp'],
    'description': """
Key Features
============
Extension for MRP to support:

* Check planning grouped by production order / work center
* Provide details about consumable materials on workorder
* Provide Mrp Overview interface
* Add mobile / tablet interface to work order
* Allow to create back orders from mobile interface

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN':"""
Tính năng nổi bật
=================
Mô-đun ```to_mrp_workorder``` bổ sung cho ứng dụng Sản xuất các tính năng:

* Hoạch định sản xuất được nhóm theo Lệnh sản xuất/Năng lực sản xuất
* Cung cấp thông tin nguyên liệu tiêu thụ trên hoạt động sản xuất
* Cung cấp giao diện sản xuất tổng quan
* Bổ sung giao diện cho thiết bị di động tới hoạt động sản xuất
* Cho phép tạo phần dở dang trực tiếp trên giao diện di dộng

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'data': [
        'views/assets.xml',
        'views/mrp_production_views.xml',
        'views/mrp_workorder_views.xml',
        'views/mrp_workcenter_views.xml'
    ],
    'demo': [
        'data/mrp_production_demo.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
