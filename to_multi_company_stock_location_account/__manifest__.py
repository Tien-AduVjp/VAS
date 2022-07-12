{
    'name': "Multi Company Stock Location Account",
    'name_vi_VN': "Tài Khoản Địa Điểm Kho Đa Công Ty",

    'summary': """
Add multi-company support for stock location accounts
        """,
    'summary_vi_VN': """
Thêm hỗ trợ đa công cy cho các tài khoản địa điểm kho
        """,

    'description': """
The problem
===========
In Odoo, with Inventory Valuation enabled, when you transfer goods in/out locations (e.g. Inventory adjustment, Production)
that have Stock Valuation Accounts specified, Odoo will also generate accounting journal entries automatically based on those stock valuation accounts.

However, these Stock Valuation Accounts fields of the stock location model do not respect multi-company enviroment.
In other words, every inventory adjustment move will be encoded into the same company's accounts no matter the company of the adjustment is.

The solution
============

* This module fixes the above problem by supporting multi-company environment for stock location's valuation accounts.
* With this module, every inventory adjustment / manufaturing moves now respect the company of the operation

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Vấn đề
======
Trong Odoo, với định giá tồn kho được bật, khi bạn dịch chuyển hàng hóa vào/ra địa điểm (VD: Điều chỉnh hàng tồn kho, sản xuất)
có tài khoản định giá kho được chỉ định, Odoo cũng sẽ tự động tạo các bút toán sổ nhật ký dựa trên các tài khoản định giá kho đó.

Tuy nhiên, Các trường tài khoản định giá kho của mô hình địa điểm kho không làm việc trong môi trường đa công ty.
Nói cách khác, mỗi động thái điều chỉnh hàng tồn kho sẽ được mã hóa vào cùng một tài khoản của công ty, bất kể công ty điều chỉnh là gì.

Giải pháp
=========

* Module này khắc phục vấn đề trên bằng cách hỗ trợ môi trường đa công ty cho các tài khoản định giá của của công ty.
* Với module này, mọi hoạt động điều chỉnh/sản xuất giờ đây đều có hoạt động của công ty.

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp
    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Warehouse',
    'version': '1.0.0',

    'depends': ['stock_account'],

    'data': [
        'views/stock_location_view.xml',
        'data/stock_location_data.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
