{
    'name': "Equipment & Parts",

    'summary': """Manage equipments and parts in hierarchy structure.
        """,

    'summary_vi_VN': """Quản lý các thiết bị và các thành phần theo phân cấp phả hệ.
        """,

    'description': """
What it does
============
* An equipment could be apart of another equipment
* View equipment and its direct parts in the form
* View equipment and its recursive parts (parts of parts) in the form
* Search Equipment by Parts
* Search Parts by Equipment
* Groups parts by equipment

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Một thiết bị có thể là một phần của thiêt bị khác.
* Hiển thị thiết bị và các thành phần trực tiếp cũng như đệ quy của thiết bị đó trên giao diện.
* Tìm kiếm thiết bị từ các thành phần.
* Nhóm các phần theo thiết bị.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Operations/Maintenance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

    # always loaded
    'data': [
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 49.5,
    'currency': 'EUR',
    'license': 'OPL-1',
}
