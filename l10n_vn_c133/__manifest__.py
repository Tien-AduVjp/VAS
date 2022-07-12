{
    'name' : 'Vietnam Chart of Accounts - Circular No. 133/2016/TT-BTC',
    'name_vi_VN' : 'Hệ thống Tài khoản Thông tư 133/2016/TT-BTC',

    'summary': 'Vietnam Chart of Accounts according to Circular #133/2016/TT-BTC by the Ministry of Finance',
    'summary_vi_VN': 'Hoạch đồ kế toán Việt Nam theo thông tư 133/2016/TT-BTC',

    'description': """
Vietnam Chart of Accounts - Circular No. 133/2016/TT-BTC
========================================================
* Create a Vietnam Chart of Accounts according to Circular #133/2016/TT-BTC

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Hoạch đồ kế toán Việt Nam theo thông tư 133/2016/TT-BTC
=======================================================
* Tạo một Hoạch đồ kế toán Việt Nam theo thông tư 133/2016/TT-BTC

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category' : 'Localization',
    'version' : '0.1.2',
    'depends' : ['l10n_vn_common', 'to_account_financial_income'],
    'data' : [
        'data/l10n_vn_c133_chart_data.xml',
        'data/account.account.template.csv',
        'data/l10n_vn_c133_chart_post_data.xml',
        'data/account_chart_template_data.xml',
        'data/account_tax_template_data.xml',
        'views/report_accounting_circular_desc_layout.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
