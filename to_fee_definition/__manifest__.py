# -*- coding: utf-8 -*-
{
    'name': "Fee Definition",
    'name_vi_VN': "Định Nghĩa Phí",
    
    'summary': """
Define fee templates""",
    'summary_vi_VN': """
Định nghĩa các mẫu phí""",

    'description': """
Key Features
============
This is the base module for other fee related modules to extend (e.g. Sales with pre-defined fees). It offers the following:

#. Fee Definition

   * It is a document to model a fee associated a product during sales / purchases. For example, when you sell a transportation service,
     you may also want to charge the customer for road toll. In such the case, you could define your service and its associated fees as below

     * Transportation Service X: is a service product

       * Road Toll 1: is another service product that present the Road Toll
       * On the Transportation Service X, select Road Toll 1 as a fee for the Transportation Service X

#. Fee is also a Product, hence, it is seamlessly integrated with Odoo accounting
#. Nested / Recursive Fee structure support. For example,

   * Transportation Service X may have the following fees structure:

     * Dirty Cargo handling Fee at terminals. This fee is also a product in Odoo and may have its own fees defined as below

       * Environment Protection Fee
       * Cargo Stowage fee

     * Road Toll during transportation

   * When calculating fees for the Transportation Service X, this module could offer the following:

     * Direct Fees: which are Dirty Cargo handling Fee and Road Toll
     * Sub fees: Environment Protection Fee, Cargo Stowage
     * Recursive Fees: all the above

NOTE
====
Again, this module provides a solid platform for other modules to extend. The module means nothing when staying alone.

Known Issues
============
* Calculation of quantity and total amount is not correct in nested fee when changing quantity in direct fee.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Module cơ bản này dùng để cho các module khác kế thừa (vd. Sale với fees đã được định nghĩa từ trước). Nó cung cấp một số tính năng sau:

#. Định nghĩa phí

   * Đây là một tài liệu dùng để mô hình hóa một khoản phí được liên kết với một sản phẩm trong quá trình mua / bán. Ví dụ,
     khi ta bán dịch vụ vận chuyển, thì có thể ta cần thu phí đi đường của khách hàng. Trong trường hợp đó,
     ta có thể định nghĩa nó là một dịch vụ và liên kết nó đến khoản phí như sau

     * Dịch vụ vận tải X: là một loại hình dịch vụ

       * Road Toll 1: Là một loại dịch vụ khác đại diện cho phí đi đường
       * Trong dịch vụ vận chuyển X, chọn Road Toll 1 làm khoản phí của Dịch vụ Vận tải X

#. Phí được coi một sản phẩm nên được tích hợp với module Kế toán để tự động hạch toán cho phí
#. Hỗ trợ khoản phí có chứa phí con (đệ quy), ví dụ:

   * Dịch vụ Vận tải X có thể có cấu trúc phí như sau:

     * Thu phí xử lý hàng hóa không gây ô nhiễm tại bến. Phí này là một loại sản phẩm trong Odoo và nó có thể chứa các phí con của nó như sau:

       * Phí bảo vệ môi trường
       * Phí bốc dỡ hàng hóa

     * Phí đi đường trong khi vận chuyển
     * Khi tính các loại chi phí của Dịch vụ Vận tải X, module này cung cấp các tính năng sau:

       * Thu phí trực tiếp: bao gồm phí xử lý hàng hóa không gây ô nhiễm tại bến và phí vận chuyển
       * Thu các loại phí con: bao gồm phí bảo vệ môi trường, phí bốc rỡ hàng hóa
       * Phí đệ quy: bao gồm hai loại trên

CHÚ Ý
=====
Nhắc lại, module này xây dụng để cho các module khác kế thừa. Và nó không thể hoạt động độc lập.

Vấn đề hiện tại
===============
* Việc tính toán số lượng và tổng số tiền không chính xác trong phí lồng nhau khi thay đổi số lượng ở phí trực tiếp.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,


    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/fee_definition_views.xml',
        'views/product_template_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
