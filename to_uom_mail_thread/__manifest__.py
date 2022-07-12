# -*- coding: utf-8 -*-
{
    'name': "Track Changes in Units of Measure",
    'name_vi_VN':"Theo dõi thay đổi Đơn vị tính",

    'summary': """
    Add mail thread and track changes on the Unit of Measure form""",
    'summary_vi_VN': """
Theo dõi lịch sử thay đổi trên form Đơn vị tính
    """,

    'description': """
What it does
============
* Modification of Units of Measure and their conversion factors could be dangerous and may harm your business. Tracking changes (who did it, what the old value was, etc.) should protect you.
* Sometimes, communication on a Units of Measure is required. Mail thread is now available on Units of Measure.

Key Features
============
* Create the Chatter area in the Units of Measure form.
* Log all changes made to the Units of Measure : who changed it, the old - new value was, when it was changed.
* Allows users to communicate in the Chatter area: add follower, send message, attach files, etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Mô tả
=====
* Khi thay đổi thông tin trên form Đơn vị tính và tỷ lệ chuyển đổi của đơn vị tính so với đơn vị gốc có thể ảnh hưởng và làm sai lệch thông tin trên hệ thống phần mềm của Doanh nghiệp bạn.
* Theo dõi những thay đổi (ai thay đổi, thay đổi gì so với trước, v.v.) sẽ giúp bạn kiểm soát tốt hơn trước khi những sai sót xảy ra.
* Mô-đun ```to_uom_mail_thread``` bổ sung thêm vùng Chatter trên form Đơn vị tính để ghi lại lịch sử và trao đổi thông tin.

Tính năng nổi bật
=================
* Tạo vùng Chatter trên form Đơn vị tính
* Ghi lại lịch sử thay đổi Đơn vị tính: ai là người thay đổi, thay đổi nội dung nào, thời gian thay đổi.
* Cho phép trao đổi thông tin trực tiếp trên form: thêm người theo dõi, gửi tin nhắn, đính kèm, v.v.

Ấn bản được hỗ trợ
==================
1. Community Edition
2. Enterprise Edition
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['uom', 'mail'],

    # always loaded
    'data': [
        'views/product_uom.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
