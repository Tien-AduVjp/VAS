{
    'name': "Vietnam QWeb Layouts",
    'name_vi_VN': "Bố cục Qweb Việt Nam",

    'summary': """
Accounting QWeb Layouts for companies based in Vietnam
""",
    'summary_vi_VN': """
Bố cục kế toán QWeb cho các công ty có trụ sở tại Việt Nam
""",

    'description': """

    """,
    'description_vi_VN': """

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['web', 'l10n_vn'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/ir_actions_report_views.xml',
        'views/accounting_external_header_left_layout.xml',
        'views/accounting_external_footer_layout.xml',
        'views/accounting_external_layout_standard.xml',
        'views/accounting_external_layout_c200.xml',
        'views/report_common_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
