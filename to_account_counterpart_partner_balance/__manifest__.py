# -*- coding: utf-8 -*-
{
    'name': "Counterpart Partner Balance Reports",
    'name_vi_VN': "Báo cáo Số dư Đối tác theo Đối ứng tài khoản",

    'summary': """
Partner balance reports using payable and receivable counterparts""",
    'summary_vi_VN': """
Báo các công nợ đối tác sử dụng đối ứng phải thu và phải trả""",

    'description': """
Partner Balance reports in Odoo are built with data from payable and receivable accounts
while the reports offering by this module are based on the data from the counterpart of the payable and the receivable
to give another view about the original of the partner balance.

In other words, this offers more details of the debtors and creditors

Known Issues
------------
* Payments are distributed across income/expense lines although they should not be. The future implementation may fix it.
* Subsequence taxes are not considered yet. The future implementation may fix it.
* Taxes are computed based on settings on the taxes. If taxes are changed after journal entries are encoded, the report may come wrong. This is due to the limit in Odoo where there is no link between a tax line and an income/expense line of a journal entry being available

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
     'description_vi_VN': """
Báo cáo công nợ đối tác trong Odoo được xây dựng dựa trên dữ liệu từ các khoản phải thu và phải trả.
Trong đó các báo cáo do module này tạo ra dựa trên các khoản công nợ đối ứng phải thu và phải trả
để có một cách nhìn khác về các khoản công nợ đối tác gốc.

Nói cách khác, cung cấp thêm thông tin chi tiết của các khoản phải thu và phải trả

Vấn đề còn tồn đọng
-------------------
* Các khoản thanh toán không nên được phân bổ trên các dòng thu/ chi phí. Trong tương lai có thể sẽ khắc phục vấn đề này.
* Các thuế phụ thuộc không được xét đến. are not considered yet.Trong tương lai có thể sẽ khắc phục vấn đề này.
* Các loại thuế được tính toán dựa trên các quy tắc thuế. Nếu quy tắc tính toán thay đổi sau khi các bút toán sổ nhật ký được ghi nhận, các báo cáo có thể sẽ bị sai. 
Điều này là do giới hạn trong Odoo khi không có liên kết giữa dòng thuế và dòng doanh thu / chi phí của một bút toán sổ nhật ký có sẵn

Phiên bản hỗ trợ
================
1. Community Edition
2. Enterprise Edition

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_account_counterpart'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/report_ctp_partner_balance_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': False,
    'auto_install': False,
    'application': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
