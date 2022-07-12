# -*- coding: utf-8 -*-
{
    'name': "URL Shortening Tools",
    'name_vi_VN': "Công cụ rút gọn link",

    'summary': """
Tools for generating link trakers for shorter URLs and tracking ability""",

    'summary_vi_VN': """
Công cụ kỹ thuật để tạo link tracker để có URL ngắn hơn và có thể theo vết được
    	""",

    'description': """
What it does
============
This is a technical module that shortens long urls with ability to track clicks, UTM Source/Campaign/Medium. Other modules can inherit and reuse the shortened urls.

Key Features
============
* Generate link trackers from given URLs

   .. code-block:: python
   
       self.env['shorten.url.mixin'].shorten_urls(self, urls, utm_source=None, campaign=None, medium=None)

* Replace long URLs in the paragraph with shortened URLs with generated link trackers 

    .. code-block:: python
   
       self.env['shorten.url.mixin'].shorten_urls_in_text(self, text, utm_source=None, campaign=None, medium=None, max_lenth=60)

Supported Editions
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
    
Mô tả
=====
Đây là module kỹ thuật cung cấp các phương thức để rút ngắn URL, tạo link tracker có thể theo vết. Các mô-đun khác có thể kế thừa và tái sử dụng url đã rút gọn.

Tính năng nổi bật
=================
* Tạo Link Trackers từ các URL

   .. code-block::
   
       self.env['shorten.url.mixin'].shorten_urls(self, urls, utm_source=None, campaign=None, medium=None)

* Thay thế URL dài trong một đoạn văn bản thành URL ngắn với link trackers

   .. code-block::
   
       self.env['shorten.url.mixin'].shorten_urls_in_text(self, text, utm_source=None, campaign=None, medium=None, max_lenth=60)

Ấn bản được hỗ trợ
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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['link_tracker'],
    'external_dependencies' : {
        'python' : ['validators'],
    },
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
