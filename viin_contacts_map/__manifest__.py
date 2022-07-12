{
    'name': 'Contacts Map',
    'name_vi_VN': 'Bản đồ liên hệ',
    'summary': """Adds notably the map view of contacts""",
    'summary_vi_VN': """Bổ sung chế độ xem bằng bản đồ của liên hệ""",
    'description': """
What it does
============
Add a map view of personal addresses in the Contact module for authorized people (administrator, human resources officers)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Bổ sung thêm chế độ xem bằng bản đồ với địa chỉ cá nhân trong phần Liên hệ cho những người được phân quyền (quản trị viên, cán bộ nhân sự)     

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

   """,

    'version': '1.0',
    'author': 'Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': [
        'contacts',
        'viin_web_map'
    ],
    'data': [
        "views/res_partner_views.xml"
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
