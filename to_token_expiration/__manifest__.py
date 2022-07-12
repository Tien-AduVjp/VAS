{
    'name': "Token Expiration",
    'name_vi_VN': 'Thời hạn Token',

    'summary': """
Generate, manage token expiration and token refreshing""",

    'summary_vi_VN': """
Tạo và quản lý hạn token và làm mới token tự động
    	""",

    'description': """

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['resource', 'base_setup'],

    # always loaded
    'data': [
        'data/cron_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_view.xml',
        'views/rotating_token_views.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
