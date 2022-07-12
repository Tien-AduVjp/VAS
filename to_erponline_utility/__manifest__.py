{
    'name': 'ERPOnline Utility',
    'version': '1.0.2',
    'category': 'Hidden',
    'summary': 'ERPOnline Utility',
    "description": """
ERPOnline Utility
=================
This is a tool for ERPOnline/Viindoo platform. Do NOT use it if your Odoo instance is not deployed on ERPOnline/Viindoo platform

    * Replace the user preference menu item 'My Odoo.com account' with 'My Viindoo.com account' (at the top right corner)
    * Replace url of menu 'Help' with ERPOnline's url help

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
 "description_vi_VN": """
ERPOnline Utility
=================
Đây là bộ công cụ phục vụ nền tảng ERPOnline/Viindoo. KHÔNG cài đặt mô-đun này nếu hệ thống của bạn không triển khai trên nền tảng ERPOnline/Viindoo

    * Thay thế menu 'Tài khoản Odoo.com' thành 'Tài khoản Viindoo.com' (Ở thiết lập tài khoản góc trái bên trên màn hình)
    * Thay link của menu 'Help' bằng link hỗ trợ của ERPOnline

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'depends': ['mail'],
    'data': [
        'views/assets.xml',
        'views/ir_module_module_views.xml',
        'views/res_users_views.xml',
        'wizards/install_module_warning_wizard_views.xml',
        'security/ir.model.access.csv'
    ],

    'qweb': ['static/src/xml/base.xml'],
    'demo': [],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'sequence': 200,
    'images': ['static/description/main_screenshot.png'],
}
