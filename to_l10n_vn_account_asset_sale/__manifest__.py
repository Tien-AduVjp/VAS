{
    'name': "Vietnam - Account Assets Sales",
    'name_vi_VN': "Doanh Số Tài Sản Kết Toán - Việt Nam",
    'summary': """Support Account Assets Sales for Vietnamese Accounting Standards compliance""",
    'summary_vi_VN': """Hỗ trợ Doanh số Tài sản Kế toán theo Chuẩn mực Kế Toán Việt Nam (VAS)""",
    'description': """
Support Account Assets Sales for Vietnamese Accounting Standards compliance
    """,
    'description_vi_VN': """
Hỗ trợ Doanh số Tài sản Kế toán theo Chuẩn mực Kế Toán Việt Nam (VAS)
    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_l10n_vn_account_asset', 'sale'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
