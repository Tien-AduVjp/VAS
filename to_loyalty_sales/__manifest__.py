{
    'name': 'Sales Loyalty Programs',
    'name_vi_VN': 'Chương Trình Khách Hàng Thân Thiết cho Bán Hàng',

    'summary': 'Loyalty Program for Sales Management application',
    'summary_vi_VN': 'Chương trình khách hàng thân thiết cho ứng dụng quản lý bán hàng',

    'description': """
What it does
============
This module extends the module Loyalty Programs Base allowing you to define loyalty programs for your Sales Management application,
where customers earn loyalty points and get rewards while buying your products/services

Key Features
============

#. Loyalty Points: loyalty points are given to a customer each time she or he buy a product or service from you which matches a
   predefined loyalty program
#. Loyalty Reward: which is either a discount or a gift (which is a product from your product list)

   * Product name: An internal identification for this loyalty reward
   * Min. Points: the minimum number of points the customer must have to qualify for this reward
   * Point Cost: The cost of one loyalty point which will be deducted from a customer's total points each time a reward
     is given to the customer.

#. Loyalty Program: you can define different loyalty programs, one of them has some rules to reward your customers based on products,
   the products quantities and number of orders, etc

   * Points per currency unit: How many loyalty points are given to a customer based on how much the customer spend.
     For example, a program can reward your users 1 point per 1 USD they pay.
   * Points per product: How many loyalty points are given to a customer based on which products the customer buy.
     For example, a customer can get X point when they buy product Y
   * Points per order: How many loyalty points are given to a customer based on each sale/point of sales order.
     For example: they can get 2 points when buying only (with Sales Order) or 1 point when buying from a Point of Sales of yours.
   * Rewards: rewards to your customers which are either Gifts or Discounts described above, qualified based on points they
     have and a loyalty program they are applied.

#. Customer Levels: allow you to define multiple customer levels. For example: Silver Customer, Gold Customer, etc.
   A customer level could be defined with a minimum loyalty points at which the customer will be promoted to the level automatically 
#. Different Loyalty Programs for different customers
#. Different Loyalty Programs for different sales channels
#. Get insight of your loyalty performance with rich and powerful Loyalty Reports

Notes
-----
If you have Points of Sales application (point_of_sale) implemented, you may want to check out the Loyalty for Point of Sales
application (to_loyalty_pos) at https://viindoo.com/apps/app/13.0/to_loyalty_pos

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

""",
    'description_vi_VN': """
Mô tả
=====
Mô-đun này mở rộng mô-đun Chương trình khách hàng thân thiết cho phép định nghĩa chương trình khuyến mại cho ứng dụng Quản lý Bán hàng,
nơi khách hàng kiếm được điểm thưởng và nhận phần thưởng khi mua sản phẩm/dịch vụ

Tính năng nổi bật
-----------------

#. Điểm thưởng: điểm thưởng dành cho khách hàng mua một sản phẩm hoặc dịch vụ trùng khớp với điều kiện của chương trình khuyến mại
#. Quà tặng: là phiếu giảm giá hoặc quà tặng (có thể lựa chọn các sản phẩm trong danh sách sản phẩm của doanh nghiệp)

    * Tên sản phẩm: Tên nội bộ cho phần thưởng này
    * Hạn mức điểm số: Số điểm thấp nhất mà khách hàng cần có để đạt được phần thưởng
    * Số điểm bị trừ: Số điểm giảm đi mỗi lần khách hàng đổi quà tặng

#. Chương trình khách hàng thân thiết: Bạn có thể khai báo các chương trình khách hàng thân thiết với các điều kiện để đạt điểm thưởng
   dựa trên sản phẩm, số lượng sản phẩm, số lượng đơn hàng

   * Điểm trên mỗi đơn vị tiền tệ: Số lượng điểm khách hàng nhận được trên số lượng tiền đã mua. Ví dụ: chương trình có thể tặng khách
     hàng của bạn 1 điểm ứng với 1 USD khách hàng chi trả.*
   * Điểm trên mỗi sản phẩm: Số lượng điểm khách hàng nhận được dựa trên số sản phẩm đã mua. Ví dụ: Khách hàng có thể  nhận được X
     điểm khi mua sản phẩm Y
   * Điểm trên mỗi đơn hàng: Số lượng điểm khách hàng nhận được ứng với mỗi đơn hàng/đơn hàng điểm bán lẻ. *Ví dụ: Khách hàng có thể
     nhận 2 điểm khi họ chỉ mua or 1 điểm khi mua từ điểm bán lẻ của bạn.
   * Phần thưởng: Phần thưởng cho khách hàng có thể là quà tặng hoặc giảm giá, giá trị của phần thưởng phụ thuộc vào số điểm khách
     hàng đã đổi.

#. Các mức khách hàng: cho phép bạn khai báo nhiều mức khách hàng. *Ví dụ, Khách hàng bạc, Khách hàng vàng, v.v.*. Mỗi mức khách
   hàng sẽ có một hạn mức để được thăng hạng một cách tự động
#. Chương trình khuyến mại khác nhau dành cho mỗi khách hàng khác nhau
#. Chương trình khuyến mại khác nhau dành cho kênh bán hàng khác nhau
#. Nhận thông tin chi tiết về khách hàng thân thiết thông qua báo cáo

Chú ý
-----
Nếu bạn đã triển khai ứng dụng Điểm Bán lẻ (Point of Sales), bạn có thể tham khảo ứng dụng chương trình Khách Hàng Thân Thiết
cho Điểm Bán lẻ (to_loyalty_pos) tại https://viindoo.com/apps/app/13.0/to_loyalty_pos

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

""",

    'version': '1.0',
    'category': 'Sales',
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'sequence': 6,
    'depends': ['to_loyalty', 'sale'],
    'data': [
        'wizard/reward_wizard.xml',
        'views/sale_order_views.xml',
        'views/loyalty_point_report.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
