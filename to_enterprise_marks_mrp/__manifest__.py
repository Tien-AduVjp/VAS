{
    'name': "Enterprise Marks - MRP",
    'name_vi_VN': "Kích hoạt tính năng Hoạt động sản xuất",

    'old_technical_name': 'to_enterprice_marks_mrp',

    'summary': """
Activate MRP Workorder in MRP config settings""",

    'summary_vi_VN': """
Kích hoạt tính năng Hoạt động sản xuất trong Thiết lập Sản xuất""",

    'description': """
What it does
============
* In the Manufacturing module, the Work Order feature only available in the Enterprise Edition will still be displayed in the settings, but will be labeled Enterprise and cannot be selected.
* This module replaces the Enterprise label and allows activating the Work Order feature developed by Viindoo.

Key Features
============
- This module replaces Enterprise labels or Work Order feature in Manufacturing Settings
- This module provides the options to activate Work Order feature
- This module will be auto installed when you install the Manufacturing module

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Ở phân hệ Sản xuất, tính năng Hoạt động sản xuất chỉ có ở bản Enterprise sẽ vẫn hiển thị ở phần cài đặt, tuy nhiên sẽ được gắn nhãn Enterprise và không thể tích chọn.
* Mô-đun này thay thế nhãn Enterprise và cho phép tích chọn tính năng Hoạt động sản xuất do Viindoo tích hợp.

Tính năng nổi bật
=================
- Thay thế nhãn Enterprise ở tính năng Hoạt động sản xuất
- Cung cấp tùy chọn kích hoạt tính năng Hoạt động sản xuất trong Thiết lập Sản xuất
- Module sẽ được tự động cài đặt khi cài đặt phân hệ Sản xuất

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
