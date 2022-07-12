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
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    'category' : 'Localization',
    'version' : '0.1.0',

    # any module necessary for this one to work correctly
    'depends' : ['l10n_vn_c200'],

    # always loaded
    'data' : [
            # update chart of accounts
            'data/l10n_vn_c133_chart_data.xml',
            'data/account_chart.xml',
            'data/l10n_vn_c133_chart_post_data.xml',
            'data/account_chart_template_data.xml',
            'data/account_tax.xml',
            'data/account_analytic_tag_data.xml',
      ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
