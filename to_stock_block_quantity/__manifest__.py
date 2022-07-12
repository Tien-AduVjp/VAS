{
    'name': "Stock Block Quantity",
    'name_vi_VN': 'Chặn số lượng hoàn thành quá số lượng yêu cầu',

    'summary': """
This module prevents users from transferring a quantity that is more than the initial demand specified on the corresponding stock transfer document
""",
    'summary_vi_VN': """
Mô-đun này dùng để chặn dịch chuyển số lượng nhiều hơn số lượng yêu cầu trên phiếu kho 
""",

    'description': """
What it does
============

* Many enterprises do not want the transportion of an excess of goods, in order to avoid situations such as:

   * Insufficient space in inventory (e.g. for large items)
   * Incurred inventory cost for excess products
   * Risk of damage to the goods in transfer (e.g. with important, high-value items)

* This module helps enterprises choose whether to allow or block transfers with more goods transfered than the initial demand.

Key Features 
============

* After installing this module, the Configuration in the Inventory application will display a check box ```Allow process exceeded demand``` in the ```Operations Types```, 
  helping users allow or block transfers where the product quantity of "Done" products is greater than the "Initial Demand".
* On the stock picking transfer, if user input a quantity of "Done" greater than the "Initial Demand" quantity column, then user will not be able to validate it.
* This feature can apply to different Type of Operation Types such as Delivery, Internal Transfer, Manufacturing

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Nhiều doanh nghiệp không muốn xảy ra tình trạng số lượng hàng hoàn tất trên phiếu kho nhiều hơn số lượng nhu cầu ban đầu, nhằm hạn chế các tình huống như: 

   * Kho không đủ chỗ chứa (ví dụ với những mặt hàng cồng kềnh) 
   * Phát sinh chi phí tồn kho cho các sản phẩm thừa 
   * Nguy cơ hư hại hàng hóa trong quá trình vận chuyển (ví dụ với những mặt hàng quan trọng, giá trị cao) 

* Mô-đun này giúp doanh nghiệp lựa chọn cho phép hoặc chặn các phiếu kho có số lượng hàng được giao nhiều hơn số lượng nhu cầu ban đầu

Tính năng nổi bật
=================

* Sau khi cài đặt mô-đun này,  trong phần thiết lập của phân hệ Kho vận sẽ xuất hiện thêm ô tích ```Cho phép xử lý vượt quá số lượng nhu cầu``` trong mục ```Kiểu giao nhận```, 
  giúp người dùng cho phép hoặc chặn các dịch chuyển có số lượng sản phẩm "Hoàn thành" lớn hơn số lượng "Nhu cầu".
* Khi bỏ chọn ô tích này, nếu người dùng nhập số lượng "Hoàn thành" lớn hơn số lượng "Nhu cầu" ban đầu trên phiếu kho, hệ thống sẽ báo lỗi, không cho phép xác nhận dịch chuyển đó. 
* Tính năng này có thể áp dụng cho các Kiểu hoạt động khác nhau như Giao hàng, Dịch chuyển Nội bộ, Sản xuất

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'category': 'Operations/Inventory',
    'version': '1.0.0',
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': ['stock'],
    'data': [           
        'views/stock_picking_type_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 19.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
