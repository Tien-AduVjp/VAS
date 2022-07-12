{
    'name': 'Vietnam - Print Payment Receipt',
    'old_technical_name': 'to_print_payment_vi',
    'name_vi_VN': 'Việt Nam - In Phiếu Thu/Chi',

    'summary': 'Print Payment Receipts in PDF according to the Templates 01-TT/02-TT',
    'summary_vi_VN': 'Mẫu PDF Phiếu Thu/Chi, Giấy báo Nợ/Có theo mẫu 01-TT/02-TT',

    'version': '0.1.0',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Localization',
    'sequence': 11,
    'description': """
What it does
==================
Print Payment Receipts in PDF according to the following templates released under the Circular No. 200/2014/TT-BTC
dated 22 December 2014 of the Ministry of Finance.

* Template 01-TT: for receiving payments
* Template 02-TT: for sending payments

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cung cấp phiên bản Pdf Phiếu Thu/Chi, Giấy báo Nợ/Có tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam.

* Mẫu số 01-TT: Các thanh toán nhận
* Mẫu số  02-TT: Các thanh toán gửi

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'depends': ['viin_payment_mediate', 'viin_l10n_vn_account_move_print'],
    'data': [
          'views/account_payment_views.xml',
          'views/report_account_move.xml',
          'views/report_account_payment.xml',
          'views/report.xml',
      ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 27.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
