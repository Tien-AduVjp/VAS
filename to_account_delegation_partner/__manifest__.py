# -*- coding: utf-8 -*-
{
    'name': "Account Delegation Partner",
    'name_vi_VN': "Kế toán - Đối tác ủy thác",

    'summary': """
Add Delegation Partner on invoice/voucher lines""",

    'summary_vi_VN': """
Thêm trường đối tác uỷ thác vào dòng hoá đơn/biên lai
    	""",

    'description': """
What it does
============
This module adds Delegation Partner field to invoice/voucher lines so that user can select a specific partner for a line.
This will be helpful when you want to record revenue/expense on a delegation partner instead of the invoice/voucher's partner

Use case
--------

1. Requirements

   - Company to pay phone fee on behalf of its employees.
   - The payment will be debit to corresponding employee's payable account in payslip

2. Master data:

   - Create a current asset account. For example, 13881 for Vietnamese Accounting
   - Create a product Employee Phone Fee with 13881 as its expense account, no tax specified
   - Create a salary rule with the following setup (this requires either Odoo EE or the TVTMA Payroll which is published at https://apps.odoo.com/apps/modules/13.0/to_hr_payroll/)

     - Debit account: an employee payable account (e.g. 334 for Vietnamese Accounting Standards)
     - Credit account: the previously created account (i.e. 13881)
     - Salary rule's Python code

       .. code-block:: python

         result = sum(employee.env['account.move.line'].sudo().search([
             ('partner_id','=',employee.sudo().address_home_id.commercial_partner_id.id),
             ('date','>=',payslip.date_from),
             ('date','<=',payslip.date_to),
             ('account_id.code','=','13881'),
             ('parent_state','=','posted')]
             ).mapped('balance'))

3. See it in action

   - Create a vendor bill with the following data

     - Vendor: Vendor 1
     - Create several invoice lines:

       - Product: Employee Phone Fee
       - Price: any that should be greater than zero
       - Delegation partner: select a partner that link to employee's private address
   - Validate the invoice to see the following entries

     - Debit: 13881, addressing the employee partner
     - Credit: vendor payable account (e.g. 331 for Vietnamese Accounting), addressing the vendor
   - Create a payslip for the corresponding period and validate it to see an accounting entry as below

     - Debit: employee payable account (e.g. 334 for Vietnamese accounting)
     - Credit: 13881

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này sẽ thêm trường Đối tác ủy thác vào dòng hóa đơn/biên lai, người dùng có thể lựa chọn một đối tác cụ thể cho từng dòng hóa đơn/biên lai.
Việc này sẽ có ích khi bạn muốn phát sinh doanh thu/chi phí cho một đối tác ủy thác thay vì đối tác của hóa đơn/biên lai.


Tình huống thực tế
------------------

1. Yêu cầu

   - Công ty trả tiền điện thoại thay cho nhân viên của mình
   - Khoản thanh toán sẽ được ghi nợ vào tài khoản phải trả cho nhân viên tương ứng trong phiếu lương

2. Dữ liệu gốc:

   - Tạo một tài khoản tài sản ngắn hạn. Ví dụ, 13881 với Kế toán Việt Nam
   - Tạo một sản phẩm Phí điện đoạn nhân viên với tài khoản 13881 là tài khoản chi phí, không định nghĩa thuế
   - Tạo một quy tắc lương với cấu hình sau (yêu cầu ấn bản Odoo EE hoặc tính năng TVTMA Payroll được xuất bản tại https://viindoo.com/apps/app/13.0/to_hr_payroll)

     - Tài khoản nợ: tài khoản phải trả nhân viên (vd: 334 theo chuẩn mực kế toán Việt Nam)
     - Tài khoản có: tài khoản đã tạo tại bước trước (vd: 13881)
     - Mã python cho quy tắc lương

       .. code-block:: python

         result = sum(employee.env['account.move.line'].sudo().search([
             ('partner_id','=',employee.sudo().address_home_id.commercial_partner_id.id),
             ('date','>=',payslip.date_from),
             ('date','<=',payslip.date_to),
             ('account_id.code','=','13881'),
             ('parent_state','=','posted')]
             ).mapped('balance'))

3. Cách hoạt động

   - Tạo một hóa đơn nhà cung cấp với những thông tin sau

     - Nhà cung cấp: Nhà cung cấp 1
     - Tạo một vài dòng hóa đơn:

       - Sản phẩm: Phí điện thoại nhân viên
       - Giá: một số bất kỳ lớn hơn 0
       - Đối tác ủy thác: lựa chọn đối tác được gắn với địa chỉ riêng tư của nhân viên

   - Xác nhận hóa đơn để hệ thống sinh ra những phát sinh sau

     - Nợ: 13881, gắn với đối tác nhân viên
     - Có: tài khoản phải trả nhà cung cấp (vd: 331 với Kế toán Việt Nam), gắn với nhà cung cấp

   - Tạo một phiếu lương trong chu kỳ tương ứng, xác nhận phiếu lương để thấy những phát sinh sau:

     - Nợ: tài khoản phải trả nhân viên (vd: 334 với Kế toán Việt Nam)
     - Có: 13881

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
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
