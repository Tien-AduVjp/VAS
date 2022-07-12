{
    'name': "Employee Equipment & Parts",

    'summary': """
Bridging module between employees and equipment in the hierarchy
        """,

    'summary_vi_VN': """
Mô đun cầu nối giữa nhân viên và thiết bị trong hệ thống phân cấp
        """,

    'description': """
What it does
============
Bridging module between employees and equipment in the hierarchy

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô đun cầu nối giữa nhân viên và thiết bị trong hệ thống phân cấp

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
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_maintenance','to_equipment_hierarchy'],

    # always loaded
    'data': [],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
