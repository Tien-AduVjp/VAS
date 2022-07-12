# -*- coding: utf-8 -*-

{
    'name': 'Replace Loyalty Program PoS Config',
    'name_vi_VN': 'Thay thế cấu hình chương trình khách hàng thân thiết',

    'summary': 'Replace PoS Loyalty config directive',
    'summary_vi_VN': 'Thay thế cấu khách hàng thân thiết cho điểm bán hàng',
    'sequence': 6,
    
    'description': """
This module replaces the default configuration directive for Odoo PoS Loyalty with TVTMA PoS Loyalty to allow users to install TVTMA loyalty by changing PoS settings.

Editions Supported
==================
1. Community Edition
""",
    'description_vi_VN': """
Mô đun này thay thế cấu hình mặc định cho khách hàng thân thiết của Odoo bằng khách hàng thân thiết của TVTMA để cho phép người dùng cài đặt khách hàng thân thiết của TVTMA bằng cách thay đổi thiết lập điểm bán hàng.

Phiên bản hỗ trợ
==================
1. Community Edition
""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    'category': 'Hidden',
    'version': '1.0',
    
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_config_settings_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
