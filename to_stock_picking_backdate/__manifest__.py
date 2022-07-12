# -*- coding: utf-8 -*-
{
    'name': "Stock Transfers Backdate",
    'old_technical_name': 'to_stock_picking_validate_manual_time',

    'summary': """
Manual validation date for stock transfers.
        """,

    'description': """
The problem
===========
In Odoo, when you validate a stock transfer, Odoo applies the current time for the transfer date automatically which is sometimes not what you want. For example, you input data for the past.

The solution
============
This module gives the user a chance to input the transfer date manually. During validation of stock transfers,
when the user click on Validate button, a new window will be popped out with a datetime field for your input.
The default value for the field is the current datetime.

The date you input here will also be used for accounting entry's date if the product is configured with automated stock valuation.

Backdate Operations Control
---------------------------

By default, only users in the "Inventory / Manager" group can carry out backdate operations in Inventory application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.


Known issues
------------

- Since the acounting journal entry's Date field does not contain time, the backdate in accounting may not respect user's timezone,
  and may causes visual discrepancy between stock move's date and accounting date. This is also an issue by Odoo that can be reproduced as below
  
  * assume that your timezone is UTC+7
  * validate a stock transfer at your local time between 00:00 and 07:00
  * go to the corresponding accounting journal entry to find its date could be 1 day earlier than the stock transfer's date 

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

Looking for the one for Odoo 12 or earlier?
===========================================
See this: https://apps.odoo.com/apps/modules/12.0/to_stock_picking_validate_manual_time/

    """,
    'description_vi_VN': """
    
Vấn đề
======
Trong Odoo, khi bạn xác nhận dịch chuyển kho, Odoo sẽ tự động áp dụng thời gian hiện tại cho ngày dịch chuyển, điều này đôi khi không như bạn muốn. 

*Ví dụ: bạn muốn nhập dữ liệu cho quá khứ sẽ không được.*

Giải pháp
=========
Module này cho phép người dùng nhập ngày dịch chuyển kho theo cách thủ công. Trong quá trình xác nhận việc dịch chuyển kho, 
khi người dùng nhấp vào nút **Xác nhận**, một cửa sổ mới sẽ xuất hiện để bạn nhập dữ liệu ngày, giờ trong quá khứ. Giá trị mặc định cho trường là ngày giờ hiện tại.

Ngày được nhập ở đây sẽ được sử dụng cho ngày nhập kế toán nếu sản phẩm được cấu hình với tính năng định giá tồn kho tự động.

Kiểm soát hoạt động lùi ngày
----------------------------

Theo mặc định, chỉ người dùng trong nhóm **Kho vận / Người quản lý** mới có thể thực hiện các thao tác nhập ngày quá khứ trong ứng dụng Kho vận. 
Những người dùng khác phải được cấp quyền truy cập **Hoạt động Nhập ngày quá khứ** trước khi làm điều đó.


Vấn đề đã biết
--------------

- Vì trường *Ngày* của bút toán sổ nhật ký không chứa thời gian, ngày quá khứ trong kế toán có thể không tuân theo múi giờ của người dùng và có thể gây ra sự khác biệt giữa ngày chuyển kho và ngày kế toán. Đây cũng là một vấn đề của Odoo có thể sao chép lại như bên dưới
  
  * giả sử rằng múi giờ của bạn là UTC+7
  * xác nhận dịch chuyển kho vào giờ địa phương của bạn trong khoảng thời gian từ 00:00 đến 07:00
  * vào bút toán sổ nhật ký tương ứng để biết ngày của nó có thể sớm hơn 1 ngày so với ngày chuyển kho

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

    'category': 'Warehouse',
    'version': '0.3',

    'depends': ['stock_account', 'to_backdate'],

    'data': [
        'security/module_security.xml',
        'wizard/stock_picking_backdate_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'application': False,
    'installable': True,
    'auto_install': False,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
