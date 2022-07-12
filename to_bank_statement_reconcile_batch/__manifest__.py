{
    'name': "Bank Statements Reconcile Batch",

    'name_vi_VN': "Đối soát sao kê ngân hàng hàng loạt",

    
    'summary': """
This module is to reconcile multiple bank transactions rather than reconciling transactions one at a time.""",
    'summary_vi_VN': """
Mô-đun này là để đối soát nhiều giao dịch ngân hàng thay vì đối soát chỉ một giao dịch một lần.
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
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/assets.xml',
    ],

    'qweb': [
        "static/src/xml/account_reconciliation.xml",
        ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
