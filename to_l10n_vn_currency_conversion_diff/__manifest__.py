{
    'name': "Vietnam - Currency Conversion Difference Move for Payment Transaction",
    'name_vi_VN': "",

    'summary': """
Set defaut accounts according to the Vietnam accounting standards""",

    'summary_vi_VN': """
Thiết lập tài khoản kế toán mặc định theo chuẩn mực kế toán Việt Nam.
        """,

    'description': """
Upon installation of this module, all currency conversion difference journals of the Vietnam chart of accounts will updated  as follows: debit 711/ credit 811

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Khi cài module này, sổ nhật ký chênh lệch quy đổi tiền tệ sẽ được thiết lập lại các tài khoản mặc định như sau: nợ 711/ có 811

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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['to_currency_conversion_diff', 'l10n_vn'],

    # always loaded
    'data': [
    ],

    'images' : [
        'static/description/main_screenshot.png'
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
