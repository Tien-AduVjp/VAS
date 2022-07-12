{
    'name': "Bank Currency Rates - Purchase Stock",
    'name_vi_VN': "Tỷ giá ngân hàng - Mua hàng về kho",

    'summary': """
Apply bank's Exchange Rates in purchase and stock operation""",
    'summary_vi_VN': """
Áp dụng tỷ giá ngân hàng vào hoạt động mua hàng, nhập kho
        """,

    'description': """
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
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
    'category': 'Purchases',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_bank_currency_rate', 'purchase_stock'],

    # always loaded
    'data': [
    ],

    'images' : [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
