{
    'name': "Inventory Backdate",

    'summary': """
Total solution for backdate stock & inventory operations""",

    'summary_vi_VN': """
Nhập ngày trong quá khứ cho các hoạt động kho vận
    	""",

    'description': """
What it does
============
In Odoo, when you carry out stock & inventory operations such as validating a stock transfer, doing inventory adjustment, creating scrap,
Odoo applies the current date and time for the move automatically which is sometimes not what you want. 

*For example, it seems to be impossible to input datas for the past operations or make a new Odoo implementation that requires data from the past*

The solution
============
This module gives you a chance to input your desired date in the past. The following operations are currently supported with backdate

* Stock Transfer
  During validation of stock transfers, when you click on Validate button, a new window will be popped out with a datetime field for your input.
  The default value for the field is the current datetime.
* Inventory Adjustment
  When validating an inventory adjustment, a new window will be popped out with a datetime field for your input.
  The default value for the field is the current datetime, in case you don't want backdate operation.
* Stock Scrapping
  During validating a scrap from either a stock transfer or a standalone scrap order, a new window will be popped out with a datetime field for your input.
  The default value for the field is the current datetime.

The backdate you input will also be used for accounting entry's date if the product is configured with automated stock valuation.
It supports all available costing methods in Odoo (i.e. Standard Costing, Average Costing, FIFO Costing)

Backdate Operations Control
---------------------------
By default, only users in the "Inventory / Manager" group can carry out backdate operations in Inventory application.
Other users must be granted to the access group **Backdate Operations** before she or he can do it.

Known issues
------------
* Since the accounting journal entry's Date field does not contain time, the backdate in accounting may not respect user's timezone,
  and may cause a visual discrepancy between stock move's date and accounting date. This is also an issue by Odoo that can be reproduced as below

  * assume that your timezone is UTC+7
  * validate a stock transfer at your local time between 00:00 and 07:00
  * go to the corresponding accounting journal entry to find its date could be 1 day earlier than the stock transfer's date
    
Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Trong Odoo, khi bạn thực hiện các hoạt động tồn kho và kiểm kê như xác nhận chuyển kho, điều chỉnh hàng tồn kho, tạo phế liệu, Odoo sẽ tự động áp dụng ngày và giờ hiện tại cho việc di chuyển. 
* Điều này gây bất tiện cho người dùng nếu như muốn nhập dữ liệu ngày tháng trong quá khứ. *Ví dụ: khi bạn đang nhập dữ liệu cho các hoạt động trước đây hoặc khi bạn bắt đầu triển khai Odoo mới yêu cầu dữ liệu từ quá khứ. Module này giúp bạn nhập các dữ liệu quá khứ một cách dễ dàng*

Tính năng nổi bật
=================
Ứng dụng hỗ trợ bạn cập nhật lại ngày nhập dữ liệu trong các tình huống sau:

* Dịch chuyển Kho:
  Khi xác nhận một dịch chuyển kho, một cửa sổ sẽ được mở ra cho phép bạn nhập Ngày giao nhận trong quá khứ vào. Ngày mặc định là thời điểm tạo các dịch chuyển
* Điều chỉnh hàng tồn kho:
  Khi xác nhận một điều chỉnh hàng tồn kho, một cửa sổ sẽ được mở ra cho phép bạn nhập Ngày giao nhận trong quá khứ vào.
* Yêu cầu phế liệu:
  Khi xác nhận yêu cầu đưa sản phẩm bất kỳ vào kho phế liệu từ một Dịch chuyển kho hoặc Yêu cầu phế liệu độc lập,  một cửa sổ sẽ được mở ra cho phép bạn nhập Ngày nhập kho trong quá khứ vào.

Ngày giao nhận này cũng sẽ được sử dụng là ngày ghi sổ kế toán nếu sản phẩm được cấu hình với tính năng định giá tồn kho tự động
Hỗ trợ tất cả các phương pháp định giá tồn kho có sẵn trong Odoo

* Giá tiêu chuẩn
* Giá trung bình
* Định giá tồn kho bằng FIFO

Phân quyền
----------
Theo mặc định, chỉ người dùng nằm trong nhóm “Quản lý Kho/ Quản trị viên” mới có thể thực hiện thao tác này. Những người dùng khác phải được cấp quyền mới sử dụng tính năng này.

Một số vấn đề tồn đọng
----------------------
* Vì trường ngày tháng trên Bút toán sổ nhật ký không có múi giờ nên thường Ngày giao nhận lùi ngày sẽ không theo múi giờ của khách hàng.
  Điều này có thể gây ra sự khác biệt trực quan giữa ngày trong dịch chuyển kho và ngày kế toán. Vấn đề này có thể giải quyết như sau:

  * Giả sư múi giờ của bạn là UTC+7
  * Xác nhận dịch chuyển kho từ 00:00 đến 07:00 theo múi giờ dịa phương bạn
  * Đi đến Bút toán sổ nhật ký và bạn có thể thấy ngày trên bút toán sổ nhật ký có thể sớm hơn một ngày so với ngày giao nhận trên dịch chuyển kho

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_stock_picking_backdate'],

    # always loaded
    'data': [
        'wizard/stock_inventory_backdate_wizard_views.xml',
        'wizard/stock_scrap_backdate_wizard_views.xml',
        'wizard/stock_warn_insufficient_qty_scrap_views.xml',
        'views/stock_inventory_views.xml',
        'views/stock_scrap_views.xml',
    ],

    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 81.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
