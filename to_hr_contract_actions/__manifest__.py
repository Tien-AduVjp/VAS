# -*- coding: utf-8 -*-
{
    'name': "HR Contract Action Buttons",
    'name_vi_VN': "Nút hành động trên hợp đồng lao động",
    'summary': """
HR Contracts actions for better workflow control""",
    'summary_vi_VN': """
Kiểm soát quy trình hoạt động trên hợp đồng lao động tốt hơn""",
    'description': """
What it does
============
* By default, switching HR contract between states is utilized by clicking a state at the header bar. This has no problem until we do need something like a workflow control. For example, cancel a contract is not allowed when it has an unposted payslip, etc
* This module help HR Contracts actions for better workflow control.

Key Features
============
This module offers the following changes

* Add action buttons in status bar to help manage contract stages even if the contract has been disabled
* The following buttons to create a simple workflow for the contract have been added

  * New Stage:

    * Start: to start the HR contract

  * Running Stage:

    * Set as To Renew: to set the contract as 'To Renew' state
    * Close: to set the contract to Expired (closed)
    * Cancellation: to cancel the contract

  * Expired Stage:

    * Renew: to renew the contract, set the contract to Running status

  * Cancelled Stage:

    * Set to New: to set the Contract to New (Draft) state

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Mặc định, việc chuyển đổi hợp đồng lao động giữa các trạng thái được thực hiện bằng cách nhấp vào một trạng thái trên thanh tiêu đề. Điều này không có vấn đề gì cho đến khi chúng ta cần một cái gì đó như kiểm soát quy trình làm việc. Ví dụ: không được phép hủy hợp đồng lao động khi nó đã có một phiếu lương chưa vào sổ, v.v.
* Mô-đun này giúp cho việc kiểm soát quy trình hoạt động trên hợp đồng lao động tốt hơn.

Tính năng nổi bật
=================
Mô-đun này cung cấp các thay đổi sau:

* Thêm các nút hành động trong thanh trạng thái giúp quản lý các giai đoạn của hợp đồng ngay cả khi hợp đồng đã bị vô hiệu hóa.
* Các nút sau đây để tạo quy trình làm việc đơn giản cho hợp đồng lao động:

  * Giai đoạn Mới:

    * Khởi động: để bắt đầu hợp đồng lao động

  * Giai đoạn Đang chạy:

    * Đặt về chờ gia hạn: đặt hợp đồng sang tình trạng 'Chờ gia hạn'
    * Đóng: để đặt hợp đồng về trạng thái Hết hạn (đóng)
    * Hủy bỏ: để hủy hợp đồng

  * Giai đoạn Hết hạn:

    * Gia hạn: gia hạn hợp đồng, đặt hợp đồng về trạng thái Đang chạy

  * Giai đoạn Đã hủy:

    * Thiết lập về Mới: để đặt Hợp đồng sang trạng thái Mới (Bản nháp)

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
        'views/hr_contract_view.xml',
    ],
    'images' : [
        'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
