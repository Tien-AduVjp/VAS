# -*- coding: utf-8 -*-

{
    'name': 'PoS Loyalty Programs',
    'name_vi_VN': 'Chương trình Khách Hàng Thân Thiết cho Điểm Bán lẻ',

    'summary': 'Loyalty Program for the Point of Sale',
    'summary_vi_VN': 'Chương trình Khách Hàng Thân Thiết cho các Điểm Bán lẻ',

    'sequence': 6,

    'description': """
What it does
============
This module extends the module Loyalty Programs Base allowing you to define loyalty programs for your points of sales, where the customers earn loyalty points and get rewards while buying your products or services at your Points of Sales.

Key Features
============
#. Loyalty Points: loyalty points are given to customers each time they buy something from you which matches a predefined loyalty program
#. Loyalty Reward: which is either a discount or gift (which is a product in your system)

   * Name: An internal identification for this loyalty reward
   * Mim. Points: the minimum number of points the customer must have to qualify for this reward
   * Point Cost: The cost of one loyalty point which will be deducted from the customer's total point each time a reward is given to the customer.

#. Loyalty Program: you can define different loyalty program, each has some rules to reward your customer based on the product, the product quantity, number of orders, etc

   * Points per currency unit: How many loyalty points are given to the customer by sold currency. *For example, the program can reward  the customers 1 point per 1 USD they pay.*
   * Points per product: How many loyalty points are given to the customer by product sold. *For example, the customer can get X point when they buy product Y.*
   * Points per order: How many loyalty points are given to the customer for each sale/point of sales order. *For example, they can get 2 point when buying only (with Sales Order) or 1 point when buying from a Point of Sales of yours.*
   * Rewards: The rewards for your customers which is either Gift or Discount above described, qualified based on the points they have and the loyalty program they are applied.

#. Customer Levels: allows you to define multiple customer level *(e.g. Silver Customer, Gold Customer, etc)*. A customer level could be defined with a minimum loyaty points at which the customer will be promoted to the level automatically
#. Get insight of your loyalty performance with abundant and powerful Loyalty Reports

Notes
-----
If you have Sales Management application implemented, you may want to check out the Loyalty for Sales application at https://viindoo.com/apps/app/13.0/to_loyalty_sales

Supported Editions
==================
Community Edition

""",
    'description_vi_VN': """
Mô tả
=====
Đây là mô-đun mở rộng cho chương trình khách hàng thân thiết.
Người sử dụng khai báo các chương trình khách hàng thân thiết cho điểm bán hàng, nơi khách hàng có thể tích lũy điểm thưởng và nhận phần thưởng khi giao dịch và sử dụng các dịch vụ tại điểm bán hàng.

Tính năng nổi bật
=================
#. Điểm thưởng: tặng cho khách hàng mỗi khi họ mua sản phẩm, dịch vụ phù hợp với chương trình khách hàng thân thiết được thiết lập trước
#. Phần thưởng: là giảm giá, quà tặng hoặc là sản phẩm

   * Tên: Một định danh nội bộ cho phần thưởng
   * Số điểm tối thiểu: Số điểm thưởng tối thiểu mà khách hàng cần có cho phần thưởng này.
   * Chi phí điểm thưởng: Số điểm giảm đi mỗi lần khách hàng đổi quà tặng

#. Chương trình khách hàng thân thiết: Bạn có thể khai báo các chương trình khách hàng thân thiết với các điều kiện để  đạt điểm thưởng dựa trên sản phẩm, số lượng sản phẩm, số lượng đơn hàng,...

  * Điểm trên mỗi đơn vị tiền: Là số điểm thưởng tặng khách hàng dựa trên số tiền thanh toán. *Ví dụ: Chương trình sẽ thưởng khách hàng 1 điểm trên 1 đô là họ trả.*
  * Điểm trên mỗi sản phẩm: Là số điểm thưởng tặng khách hàng dựa trên sản phẩm bán ra. *Ví dụ: Khách hàng có thể nhận X điểm khi họ mua sản phẩm Y.*
  * Điểm trên mỗi đơn hàng: Số điểm thưởng tặng khách hàng dự trên mỗi đơn hàng bán hoặc đơn điểm bán. *Ví dụ: Khách hàng có thể nhận 2 điểm khi có đơn hàng mua hoặc 1 điểm khi mua từ điểm bán.*
  * Phần thưởng: Phần thưởng có thể là giảm giá hoặc quà tặng như đã khai báo ở trên, giá trị dựa trên số điểm khách hàng có hoặc chương trình được áp dụng.

#. Hạng mức khách hàng: Cho phép khai báo nhiều mức hạng *(Ví dụ: Khách hàng bạc, Khách hàng vàng, v.v.)*. Khách hàng có thể tự động nâng hạng khi thỏa mãn điều kiện số điểm tối thiểu.
#. Nhận dữ liệu thông tin hiệu suất chi tiết bằng các Báo cáo về mức độ thân thiết phong phú và đầy đủ

Chú ý
-----
Nếu bạn đã triển khai ứng dụng Quản lý bán hàng, bạn có thể tham khảo ứng dụng Khách Hàng Thân Thiết cho Quản Lý Bán Hàng tại https://viindoo.com/apps/app/13.0/to_loyalty_sales

Ấn bản được hỗ trợ
==================
Ấn bản Community
""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'version': '1.0',
    'category': 'Point of Sale',

    'depends': ['to_loyalty', 'to_pos_refund_origin', 'to_replace_loyalty_pos_config'],

    'data': [
        'security/pos_loyalty_security.xml',
        'views/pos_config_views.xml',
        'views/pos_loyalty_views.xml',
        'views/pos_loyalty_templates.xml',
        'views/loyalty_point_report.xml',
    ],
    'qweb': [
        'static/src/xml/Screen/ProductScreen/ProductScreen.xml',
        'static/src/xml/Screen/ProductScreen/OrderWidget.xml',
        'static/src/xml/Screen/ProductScreen/LoyaltyPoints.xml',
        'static/src/xml/Screen/ReceiptScreen/OrderReceipt.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
