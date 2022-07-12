{
    'name': "Vietnam - Account Asset",
    'name_vi_VN': "Tài sản Kế toán - Việt Nam",
    'summary': """
Support Account Assets Management according to Vietnam Accounting Standards (VAS)""",
    'summary_vi_VN':"""
Hỗ trợ Quản lý Tài sản Kế toán theo Chuẩn mực Kế Toán Việt Nam (VAS)""",
    'description': """
Key Features:
=============
* Fix depreciation computation according to Vietnam Accounting Standards
* Support assets sold/disposed in the way in compliance with VAS

Example of a Full Process Demonstration (with sale/disposal activity)
----------------------------------------------------------------------
Assumes the asset is purchased at the price of 1200 (in company currency)

* Validate Vendor Bill when purchase Asset:

    * D.151: 1200
    * C.331: 1200
    * Payment:

        * D.331: 1200
        * C.111: 1200

* Move asset into stock:

    * D.211: 1200
    * C.151: 1200

* Asset Depreciation:

    * D.642: 100
    * C.214: 100

* Asset Disposal/Sale:

    * D.811: 1100
    * C.214: 1100

* Validate Customer Invoice (assume sold at 2000 VND):

    * D.131: 2000
    * C.711: 2000

        * Payment:

            * D.111: 2000
            * C.131: 2000

* Asset Out from the Stock:

    * D.214: 1200
    * C.211: 1200 

Balance:

* 811: 1100 (debit)
* 214: 0
* 211: 0
* 711: 2000 (credit)
* 151: 0
* 131: 0
* 331: 0
* 111: 800 (debit)
* 642: 100 (debit)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng chính:
================
* Ấn định cách tính khấu hao theo Chuẩn mực kế toán Việt Nam
* Hỗ trợ bán/thanh lý tài sản tuân thủ theo Chuẩn mực kế toán Việt Nam (VAS)

Ví dụ đầy đủ về quy trình bán/thanh lý tài sản
----------------------------------------------
Giả sử tài sản được mua với giá 1200 (theo đơn vị tiền tệ của công ty)

* Xác thực Hoá đơn của Nhà cung cấp khi mua Tài sản:

     * Nợ 151: 1200
     * Có 331: 1200

        * Payment:

            * Nợ 331: 1200
            * Có 111: 1200

* Chuyển tài sản vào kho:

    * Nợ 211: 1200
    * Có 151: 1200

* Tài sản Khấu hao:

    * Nợ 642: 100
    * Có 214: 100

* Thanh lý/Bán Tài sản:

    * Nợ 811: 1100
    * Có 214: 1100

* Xác thực Hoá đơn của Khách hàng (giả sử được bán với giá 2000 VND):

    * Nợ 131: 2000
    * Có 711: 2000

        * Thanh toán:

            * Nợ 111: 2000
            * Có 131: 2000

* Tài sản xuất ra khỏi Kho:

    * Nợ 214: 1200
    * Có 211: 1200 
    
Bảng cân đối:

* 811: 1100 (ghi nợ)
* 214: 0
* 211: 0
* 711: 2000 (ghi có)
* 151: 0
* 131: 0
* 331: 0
* 111: 800 (ghi nợ)
* 642: 100 (ghi có)

Các ấn bản hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['to_account_asset', 'l10n_vn_c200', 'to_base', 'to_l10n_vn_qweb_layout'],

    # always loaded
    'data': [
        'views/account_asset_card_s23dn.xml',
        'views/report_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
