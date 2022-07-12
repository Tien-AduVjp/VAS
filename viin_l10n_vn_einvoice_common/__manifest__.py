{
    'name': 'Vietnam - E-invoice',
    'name_vi_VN': 'Việt Nam - Hóa đơn điện tử',

    'summary': """Provide localization tools to handle E-invoice according to Vietnam rules""",
    'summary_vi_VN': """Cung cấp công cụ bản địa hóa để xử lý hóa đơn điện tử theo quy định của Việt Nam""",

    'description': """
What it does
============
This module aims to provide localization tools to handle E-invoice according to Vietnam rules.

Known Issues
------------
* On E-invoices, product names are always vietnamese. If issuing e-invoices for foreigners needs english name, we will add endlish name 
  right after vietnamese name and in parentheses.
* Not allow newline characters in product names
  
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cung cấp công cụ bản địa hóa để xử lý hóa đơn điện tử theo quy định của Việt Nam.

Vấn đề còn tồn đọng
-------------------
* Trên hóa đơn điện tử, tên sản phẩm luôn là tiếng Việt. Nếu xuất hóa đơn điện tử cho người nước ngoài cần có tên tiếng Anh, chúng tôi sẽ thêm tên tiếng Anh
  ngay sau tên tiếng việt và trong ngoặc đơn.
* Không cho phép các ký tự xuống dòng trong tên sản phẩm
  
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    'category': 'Localization',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['l10n_vn', 'to_einvoice_common'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
