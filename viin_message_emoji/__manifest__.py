{
    'name': "Message Emoji",
    'name_vi_VN': "Biểu tượng Cảm xúc cho Tin nhắn",
    'version': '0.1.0',
    'summary': """Message emoji feature for Discuss""",
    'summary_vi_VN': """
        Tính năng biểu tượng cảm xúc cho tin nhắn
    	""",
    'description': """
What it does
============
This modules:

* Provide emoji feature on messages
* Allows users to add emojis on other people's messages


Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Module này:

* Cung cấp tính năng biểu tượng cảm xúc trên tin nhắn
* Cho phép người dùng thể hiện cảm xúc trên tin nhắn của người khác

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/emoji.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/thread_emoji.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
