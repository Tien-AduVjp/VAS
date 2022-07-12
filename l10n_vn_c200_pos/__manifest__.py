{
    'name': "PoS - c200 Fix",
    'name_vi_VN': "PoS - Sửa đổi tài khoản theo thông tư 200",

    'summary': """
Fix Wrong account in PoS Payment Methods for Vietnam based companies""",
    'summary_vi_VN': """
Sửa đổi tài khoản phải thu của khách hàng từ 132 thành 131 theo thông tư 200 cho các công ty Việt Nam""",

    'description': """
Key Features
============
* Fix Wrong account in PoS Payment Methods for Vietnam based companies

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """

Tính năng nổi bật
=================
* Cho phép sửa đổi tài khoản phải thu của khách hàng từ 132 thành 131 theo thông tư 200 cho các công ty Việt Nam

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version' : '0.1.0',
    'depends': ['l10n_vn_c200', 'point_of_sale'],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
