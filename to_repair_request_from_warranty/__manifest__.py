# -*- coding: utf-8 -*-
{
    'name': "Repair Request from Warranty Claim",
    'old_technical_name': 'to_repair_request_from_waraantee',
    'name_vi_VN': "Yêu cầu sửa chữa từ yêu cầu bảo hành",
    'summary': """
Generate a Repair Order from a Warranty Claim
        """,
    'summary_vi_VN':"Tạo Đơn sửa chữa từ Yêu cầu bảo hành",
    'description': """
What it does
============
This module helps create Repair Order from Warranty Claim

* Add the button "Create repair order" on Warranty Claim form
* Show the list of Repair orders related to Warranty Claim

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này cho phép tạo Lệnh sửa chữa từ Yêu cầu bảo hành

* Thêm nút hành động "Tạo lệnh sửa chữa" trên form Yêu cầu bảo hành
* Thống kê danh sách Lệnh sửa chữa liên quan đến yêu cầu bảo hành

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['to_warranty_management', 'viin_repair'],
    'data': [
        'security/ir.model.access.csv',
        'views/warranty_claim_view.xml',
        'views/repair_order_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
