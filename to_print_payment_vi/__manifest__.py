# -*- coding: utf-8 -*-

{
    'name': 'Vietnam - Payment Receipt/Voucher and General Voucher',
    'name_vi_VN': 'Việt Nam - Phiếu Thu/Chi và Phiếu kế toán',
    
    'summary': 'Print Payment Receipts and General Voucher in PDF according to the Templates 01-TT/02-TT',
    'summary_vi_VN': 'Mẫu PDF Phiếu Thu/Chi, Giấy báo Nợ/Có và Phiếu kế toán theo mẫu 01-TT/02-TT',
    
    'version': '0.1',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
   
    'category': 'Localization',
    'sequence': 11,
    'description': """
What it does
==================
Print Payment Receipts and General Voucher in PDF according to the following templates released under the Circular No. 200/2014/TT-BTC
dated 22 December 2014 of the Ministry of Finance.

* Template 01-TT: for receiving payments
* Template 02-TT: for sending payments
* General Voucher

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Ứng dụng này làm gì
===================
Ứng dụng này cung cấp phiên bản Pdf Phiếu Thu/Chi, Giấy báo Nợ/Có và Phiếu kế toán tuân thủ Thông tư số 200/2014 / TT-BTC ngày 22 tháng 12 năm 2014 của Bộ Tài chính Việt Nam.

* Mẫu số 01-TT: Những thanh toán nhận
* Mẫu số  02-TT: Những thanh toán gửi
* Phiếu kế toán
Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    'depends': ['viin_payment_mediate', 'to_vietnamese_number2words', 'to_l10n_vn_qweb_layout', 'account'],
    'data': [
          'views/account_payment_view.xml',
          'views/report_general_voucher_views.xml',
          'views/report_accountpayment.xml',
          'views/report_view.xml',
      ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}

