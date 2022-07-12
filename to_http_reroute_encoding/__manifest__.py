{
    'name': "Http Reroute Encoding",
    'name_vi_VN': "Mã hóa URL khi Định tuyến lại",
    'summary': """Fix URL encoding error on rerouting""",
    'summary_vi_VN': """Sửa lỗi mã hóa URL khi định tuyến lại""",
    'description': """
The problem
===========
For multi language website, when request http:/localhost/en/something, Odoo  reroutes from the requested path "/en/something" to the new path "/something" with lang=en_US in context.

If the new path is a unicode string like "/xin-chào", a error should occur at werkzeug._compat.wsgi_decoding_dance() because the path was not latin1 string.

Related issue: https://github.com/odoo/odoo/issues/25176

The Solution
============
This module fixes the issue by converting the path to latin1 using corresponding wsgi_encoding_dance() before it is passed to wsgi_decoding_dance().

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======
Đối với trang web đa ngôn ngữ, khi có yêu cầu đến http://localhost/en/something, Odoo định tuyến lại từ đường dẫn được yêu cầu "/en/something" đến đường dẫn mới "/something" với lang=en_US trong ngữ cảnh.

Nếu đường dẫn mới là một chuỗi unicode như "/xin-chào", lỗi sẽ xảy ra tại werkzeug._compat.wsgi_decoding_dance() vì đường dẫn không phải là chuỗi latin1.

Vấn đề liên quan: https://github.com/odoo/odoo/issues/25176

Giải pháp
=========
Mô-đun này khắc phục sự cố bằng cách chuyển đổi đường dẫn thành chuỗi latin1 bằng cách sử dụng wsgi_encoding_dance() tương ứng trước khi nó được chuyển đến wsgi_decoding_dance().

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
    'category': 'Extra Tools',
    'version': '0.1',
    'depends': ['http_routing'],
    'data': [],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
