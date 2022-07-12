# -*- coding: utf-8 -*-

{
    'name': 'Import RJE Bank Statement',
    'name_vi_VN': 'Nhập Sao kê điện tử ngân hàng - RJE',
    'summary': 'Import Bank Statement at RJE format',
    'summary_vi_VN': 'Nhập sao kê ngân hàng ở định dạng RJE',
    
    'description': """
What it does
============
This module is to import RJE bank statements.

Key Features
============
* This module allows you to import RJE files (SWIFT MT940 format) in Odoo: they are parsed and stored in human readable format in
  Accounting \ Bank and Cash \ Bank Statements.

* Known Issue
  Because of the RJE format limitation, we can't ensure whether the same transactions are imported several times or handled by related partners.
  You must manually check the imported bank statement before taking the reconciliation.
  Whenever possible, you should use a more appropriate file format, like OFX.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",
    
    'description_vi_VN': """
Mô tả
=====
Mô-đun này hỗ trợ việc nhập bảng sao kê điện tử ngân hàng ở định dạng RJE vào hệ thống Odoo.

Tính năng nổi bật
=================
* Cho phép bạn nhập các tài liệu ở định dạng RJE (SWIFT MT940) trong Odoo: phân tích cú pháp và lưu trữ các tài liệu đó ở định dạng người dùng có thể đọc được, trong Kế toán\ Ngân hàng và Tiền mặt\ Sao kê ngân hàng.

* Vấn đề có thể phát sinh: 
  Do tính hạn chế của định dạng RJE, chúng tôi không thể đảm bảo việc các giao dịch giống nhau là do được nhập nhiều lần hay được xử lý bởi nhiều đối tác liên quan. 
  Bạn cần kiểm tra thủ công các bảng sao kê đã được nhập lên hệ thống trước khi tiến hành đối soát. 
  Bất cứ khi nào có thể, hãy sử dụng định dạng phù hợp hơn, ví dụ OFX.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",
    
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Accounting/Accounting',
    'version': '1.0',
    'depends': ['account_bank_statement_import', 'base_import'],
    'data': [
        'wizard/account_bank_statement_import_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'external_dependencies' : {
        'python' : ['mt-940'],
    },
    
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 199.8,
    'currency': 'EUR',
    'license': 'OPL-1',
}
