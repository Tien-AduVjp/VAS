{
    'name': "Enterprise Marks - Inter-Company",
    'name_vi_VN': 'Kích hoạt chức năng đa công ty',
    'old_technical_name': 'to_enterprice_marks_inter_company',
    'summary': """Replace Enterprise Edition marks regarding Inter-Company flows""",

    'summary_vi_VN': """
Thay thế tuỳ chọn kích hoạt tính năng Quy trình liên công ty mặc định của Odoo EE với Quy trình liên công ty của Viindoo
    	""",

    'description': """
What it does
============
When using the Community edition, some features that are only available in the Enterprise edition will still be visible in the settings,
but will be labeled Enterprise and cannot be selected. If these features can be used with one or more alternative modules developed by Viindoo,
this module will replace the Enterprise labels and directs the user to the settings of those features.

Key Features
============
* This module provides the options to enabling inter-company transaction features
* This module will be auto installed

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Khi sử dụng ấn bản Community, một số các tính năng chỉ có ở bản Enterprise sẽ vẫn hiển thị ở phần cài đặt,
tuy nhiên sẽ được gắn nhãn Enterprise và không thể tích chọn. Nếu những tính năng này có thể được sử dụng
với một hoặc nhiều mô-đun thay thế khác do Viindoo phát triển, mô-đun này sẽ thay thế các nhãn Enterprise
và điều hướng người dùng đến phần cài đặt của những tính năng đó.

Tính năng nổi bật
=================
* Module cung cấp tùy chọn thiết lập để kích hoạt tính năng giao dịch liên công ty
* Module được cài đặt tự động

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_setup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
