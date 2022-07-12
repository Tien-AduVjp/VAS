# -*- coding: utf-8 -*-
{
    'name': "Slugify Vietnamese",
    'name_vi_VN': "Slugify Tiếng Việt",
    
    'summary': """Monkey patch build-in slugify to better support Vietnamese""",
    'summary_vi_VN': """Cải tiến hàm slugify để hỗ trợ tiếng Việt tốt hơn""",
    
    'description': """Transform a string include "đ" or "Đ" characters to a slug that can be used in a url path""",
    'description_vi_VN': """Chuyển đổi chuỗi bao gồm chữ "đ" hoặc "Đ" để sử dụng làm đường dẫn""",
    
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.1',
    'depends': ['http_routing'],
    'data': [],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
