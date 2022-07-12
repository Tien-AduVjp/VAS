{
    'name': "Bank Currency Rates",
    'name_vi_VN': "Tỷ Giá Tiền Tệ Theo Ngân Hàng",
    
    'summary': """
Currency conversions with specific bank' Exchange Rates""",
    'summary_vi_VN': """
Quy đổi tiền tệ theo tỷ giá ngân hàng cụ thể
    """,

    'description': """
The problem
===========
Odoo currency conversion does not respect the actual rate of the bank where the transaction happens

Solutions
=========

This module adds the following features to Odoo

1. Rate is now able to be specified with bank and exchange type which is either Sell Rate or Buy Rate
2. Currency conversion now respect the rate of the bank where the transaction happens. In case no bank is specified, it will fall back to the company main bank which is specified under Accounting's settings

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======
Mặc định, việc quy đổi tỷ giá của Odoo không theo bất cứ ngân hàng nào. Người dùng buộc phải ngầm định một ngân hàng khi nhập tỷ giá. Tuy nhiên, điều này gây rắc rối khi doanh nghiệp giao dịch ngoại tệ ở nhiều ngân hàng khác nhau với các tỷ giá khác nhau. Hoạt động mua bán ngoại tệ cũng dùng các tỷ giá mua và bán khác nhau ở cùng một ngân hàng

Giải pháp
=========

Module này bổ sung các tính năng sau vào Odoo

1. Khi nhập tỷ giá, người dùng có thể chọn ngân hàng và kiểu tỷ giá (Mua hoặc Bán) để xác lập tỷ giá cho từng ngân hàng ứng với từng hoạt động Mua hoặc Bán ngoại tệ
2. Khi quy đổi tỷ giá, nếu ngân hàng được xác định thì sẽ sử dụng tỷ giá của ngân hàng đó. Trong trường hợp không xác định thì sẽ sử dụng tỷ giá của ngân hàng chính mà được thiết lập ở phần Thiết lập của ứng dụng Kế toán.

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
    'category': 'Accounting',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['account', 'to_currency_rate'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_bank_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_currency_rate_views.xml',
    ],

    'images' : [
    	'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
