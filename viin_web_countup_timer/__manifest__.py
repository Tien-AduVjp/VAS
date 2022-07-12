# -*- coding: utf-8 -*-
{
    'name': "Countup Timer Widget",
    'name_vi_VN': "Bộ đếm tăng thời gian",

    'summary': """Count up timer widget for datetime fields""",
    'summary_vi_VN': """
Cung cấp widget đếm tăng thời gian cho các trường Datetime
    	""",

    'description': """
Key Features
============
This module offers a new field widget to show count up timer for datetime fields

Syntax
------

.. code-block:: xml

  <field name="a_datetime_field" widget="countup_timer" />

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Mô-đun này cung cấp widget mới đếm tăng thời gian cho các trường Datetime

Syntax
------

.. code-block:: xml

  <field name="a_datetime_field" widget="countup_timer" />
  
Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

  """,

    'author': "Viindoo",
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
    'depends': ['web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
    ],

    'images': [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 18.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
