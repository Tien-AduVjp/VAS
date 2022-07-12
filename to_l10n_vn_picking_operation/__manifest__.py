{
    'name': "Vietnam Receipt/Delivery Order Templates",
    'name_vi_VN': "In phiếu Nhập/Xuất kho theo mẫu Việt Nam ",
    'summary': """
Goods Receipts and Delivery Orders Templates according to the Circular No. 200/2014/TT-BTC
        """,

    'summary_vi_VN': """
In phiếu Xuất kho, Nhập kho theo mẫu thông tư 200/2014/TT-BTC.
    	""",

    'description': """
This module replaces the Odoo standard Picking Operation template with the templates VT-01 (for Receipts) and VT-02 (for Delivery Orders) according to the Circular No. 200/2014/TT-BTC by the Ministry of Finance.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô-đun này thay thế mẫu Xuất, Nhập kho tiêu chuẩn của Odoo bằng các mẫu VT-01 (đối với Phiếu Nhập Kho) và VT-02 (đối với Phiếu Xuất Kho) theo Thông tư số 200/2014 / TT-BTC của Bộ Tài chính.

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
    'category': 'Warehouse Management',
    'version': '0.1',
    'depends': [
        'to_base',
        'to_vietnamese_number2words',
        'to_stock_account_moves_link',
        'sale_stock',
        'purchase_stock',
        'to_l10n_vn_qweb_layout',
],
    'data': [
        'views/stock_picking_views.xml',
        'report/picking_operation_report_templates.xml',
    ],
    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
