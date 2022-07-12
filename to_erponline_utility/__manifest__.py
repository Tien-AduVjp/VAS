{
    'name': 'ERPOnline Utility',
    'version': '1.0.2',
    'category': 'Hidden',
    'summary': 'ERPOnline Utility',
    "description": """
ERPOnline Utility
=================
This is a tool for ERPOnline/Viindoo platform. Do NOT use it if your Odoo instance is not deployed on ERPOnline/Viindoo platform

    * Remove menu 'My Odoo.com account'
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

    * Xóa menu 'My Odoo.com account'
    * Thay link của menu 'Help' bằng link hỗ trợ của ERPOnline

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': ['mail'],
    'data': [
        'views/assets.xml',
        'views/ir_module_module_views.xml',
        'views/res_users_views.xml',
        'wizards/install_module_warning_wizard_views.xml',
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
