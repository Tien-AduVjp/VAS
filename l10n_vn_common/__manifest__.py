{
    'name': 'Vietnam Chart of Accounts',
    'name_vi_VN': 'Hệ thống Tài khoản Kế toán Việt Nam',

    'summary': 'Vietnam Chart of Accounts',
    'summary_vi_VN': 'Hoạch đồ kế toán Việt Nam',

    'description': """
What it does
============
This module allows:

#. This is the base module to manage the generic accounting chart in Viet Nam

#. Accounting QWeb Layouts for companies based in Vietnam

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Mô đun này cho phép:

#. Đây là mô-đun cơ sở để quản lý hoạch đồ kế toán Việt Nam

#. Bố cục kế toán QWeb cho các công ty có trụ sở tại Việt Nam

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Localization',
    'version': '0.1.0',
    'depends': ['web', 'l10n_vn', 'to_tax_is_vat'],
    'data': [
        'data/account_account_tag_data.xml',
        'data/account_analytic_tag_data.xml',
        'data/account_chart_template_data.xml',
        'data/account_group_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_report_line_data.xml',
        'data/account_tax_template_data.xml',
        'data/report_paperformat_data.xml',
        'views/account_account_views.xml',
        'views/ir_actions_report_views.xml',
        'views/report_accounting_external_header_left_layout.xml',
        'views/report_accounting_external_footer_layout.xml',
        'views/report_accounting_external_layout_standard.xml',
        'views/report_accounting_circular_external_layout_standard.xml',
        'views/report_common_templates.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': ['l10n_vn'],
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
