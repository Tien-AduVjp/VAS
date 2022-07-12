{
    'name': "Equipment Working Frequency",
    'name_vi_VN': "Tần Suất Làm Việc Của Thiết Bị",
    'summary': """
Manage equipment working frequency""",
    'summary_vi_VN': """
Quản lý tần suất làm việc của thiết bị
    	""",
    'description': """
What it does
============
* Add new field to product to define working frequency template
* Add new field to equipment that get info from related product, user can modify the real number for each equipment

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Thêm trường để định nghĩa tần suất làm việc mặc định cho sản phẩm
* Thêm trường lấy các thông tin về tần suất làm việc mặc định trên sản phẩm cho thiết bị, người dùng có thể thay đổi con số thực tế đối với mỗi thiết bị


Ấn bản hỗ trợ
=============
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',

    'depends': ['to_equipment_maintenance_schedule'],

    # always loaded
    'data': [
        'data/uom_data.xml',
        'security/ir.model.access.csv',
        'views/working_frequency_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
