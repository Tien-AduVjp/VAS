{
    'name' : 'Partner Multilingual',
    'name_vi_VN': "Đa ngôn ngữ thông tin đối tác",
    'version': '1.0.1',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'summary': "Translate Partners' Information",
    'summary_vi_VN': """
Dịch các thông tin đối tác""",
    'sequence': 30,
    'category': 'Technical Settings',
    'description':"""
Key Features
=============
This module allows users to translate the below information:

* Partner name
* Bank name
* Company name
* City/ State name

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Mô-đun này cho phép dịch các thông tin sau:

  * Tên đối tác
  * Tên ngân hàng
  * Tên công ty
  * Tên tỉnh/ thành

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['web'],
    'data': [
        #'views/assets.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_load': 'post_load',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
