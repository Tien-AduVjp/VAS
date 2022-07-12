{
    'name': "Promotion Voucher - Vietnam Accounting",
    'name_vi_VN': "Phiếu khuyến mãi - Kế toán Việt Nam ",

    'summary': """
Default promotion voucher loss & profit accounts for Vietnam""",
    'summary_vi_VN': """
Tài khoản lỗ & lãi của phiếu khuyến mãi mặc định cho Việt Nam""",

    'description': """
This is a localized application that helps Promotion Voucher application get compatible with
VAS (Vietnamese Accounting Standards)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Đây là một mô-đun bản địa hóa cho ứng dụng Phiếu khuyến mãi, giúp tương thích với
VAS (Chuẩn mực Kế toán Việt Nam) 
    
Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp
    """,
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['to_promotion_voucher', 'l10n_vn'],

    # always loaded
    'data': [
        'data/l10n_vn_chart_data.xml',
        'data/voucher_type_data.xml',
        'data/product_category_data.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
