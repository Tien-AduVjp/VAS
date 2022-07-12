# -*- coding: utf-8 -*-
{
    'name': "Website No Follow",
    'name_vi_VN': "Website No Follow",

    'summary': """
        Prevent Search Engines from indexing, following links in your Website.
                """,

    'summary_vi_VN': """
            Ngăn các Công cụ Tìm kiếm lập chỉ mục, theo dõi các liên kết trong trang web của bạn.
    	""",

    'author': 'VIINDOO TECHNOLOGY.,JSC',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'support@viindoo.com',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'templates/website_templates.xml',
        'views/res_config_settings_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    # only loaded in demonstration mode
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
