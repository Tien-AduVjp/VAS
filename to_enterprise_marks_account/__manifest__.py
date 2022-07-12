{
    'name': "Enterprise Marks - Accounting",
    'old_technical_name': 'to_enterprice_marks_account',
    'name_vi_VN': 'Kích Hoạt Chức Năng Kế toán',
    'summary': """
Replace Enterprise labels in Accounting Settings
""",
    'summary_vi_VN': """
Thay thế các nhãn của Enterprise trong Thiết lập Kế toán
        """,
    'description': """
What it does
============
In the Accounting module, some Accounting features only available in the Enterprise Edition will still be displayed in the settings, but will be labeled Enterprise and cannot be selected.
This module replaces the Enterprise label and allows activating the similar featured developed by Viindoo.

Key Features
============
- This module replaces Enterprise labels in Accounting Settings
- This module provides the options to enable accounting features
- This module will be auto installed when you install the Accounting module

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Một số tính năng ở phân hệ Kế toán chỉ có ở bản Enterprise sẽ vẫn hiển thị ở phần cài đặt, tuy nhiên sẽ được gắn nhãn Enterprise và không thể tích chọn.
Mô-đun này thay thế nhãn Enterprise và cho phép tích chọn những tính năng Kế toán thay thế do Viindoo tích hợp.

Tính năng nổi bật
=================
- Thay thế các nhãn của Enterprise trong Thiết lập Kế toán
- Cung cấp tùy chọn thiết lập để kích hoạt các tính năng thay thế trong Thiết lập Kế toán
- Module sẽ được tự động cài đặt khi cài đặt phân hệ Kế toán

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
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
