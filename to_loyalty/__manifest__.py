# -*- coding: utf-8 -*-

{
    'name': 'Loyalty Program',
    'name_vi_VN':'Khách hàng Thân thiết',

    'summary': 'Loyalty Programs Base',
    'summary_vi_VN':'Cơ sở Chương trình khách hàng thân thiết',

    'sequence': 6,

    'description': """
What it does
============
* This application is designed as the base for other loyalty applications which allows you to define loyalty programs where the customers earn loyalty points and get rewards.
* The application provides the most important data models and structures to build a great loyalty program.

**Key Features**
================
#. Set up Loyalty programs including rewards and points rounding settings of products, currencies and order units and allow customers to earn rewards or discounts from the Rewards Points fund .

   * Loyalty Points: loyalty points are given to customers each time they buy something which matches a predefined loyalty program.
   * Loyalty Reward: which is either a discount or gift (which is also a product in your Odoo)

     * Name: An internal identification for this loyalty reward
     * Mim. Points: the minimum number of points the customer must have to qualify for this reward
     * Point Cost: The cost of one loyalty point which will be deducted from the customer's total point each time a reward is given to the customer.

   *Loyalty Program: you can define different loyalty program, each has some rules to reward your customer based on the product, the product quantity, number of orders, etc

     * Points per currency unit: How many loyalty points are given to the customer by sold currency. *For example, the program can reward the customers 1 point per 1 USD they pay.*
     * Points per product: How many loyalty points are given to the customer by a quantity of product sold. *For example, the customer can get X point when they buy product Y*
     * Points per order: How many loyalty points are given to the customer for each sale/point of sales order. *For example, they can get 2 point when buying with one Sales Order or 1 point when buying from a Point of Sales of yours.*
     * Rewards: The rewards for your customers which is either Gift or Discount as described above, qualified based on the points they have and the loyalty program they are applied.

#. Create rules to get rewards points for specific products or categories
#. Do bonus points reports in different display types such as tables, charts, graphs, ...
#. Manage the Loyalty Program and assign it to the Sales team at your discretion
#. Points manual adjustment and points rounding
#. Design and automatically upgrade customer levels based on their minimum points

   * Customer Levels: allows you to define multiple customer levels *(E.g. Silver Customer, Gold Customer, etc)*. A customer level could be defined with a minimum loyaty point at which the customer will be promoted to the level automatically
   * Customer Level's Pricelist: allows synchronizing Customer Level's pricelist with the partner's pricelist

#. Ready for other applications to extend

Notes
-----
This application was designed as the technical base for other modules to extend. Eg. Loyalty for PoS, Loyalty for Sales, Loyalty for eCommerce, etc. Without those inheritances, this module does nothing.
Check out the following available applications for further details:

* to_loyalty_sales: https://viindoo.com/apps/app/13.0/to_loyalty_sales (Sales Management application required)
* to_loyalty_pos: https://viindoo.com/apps/app/13.0/to_loyalty_pos (Point of Sales application required)

Supported Editions
==================
Community Edition

""",
'description_vi_VN': """
Mô tả
=====
* Ứng dụng này được thiết kế là cơ sở cho các ứng dụng về khách hàng thân thiết, cho phép người dùng kiếm điểm thưởng và phần thưởng.
* Ứng dụng cung cấp những cấu trúc và mẫu dữ liệu quan trọng nhất để tạo nên một chương trình khách hàng thân thiết tốt.

Tính năng nổi bật
=================
#. Thiết lập các chương trình Khách Hàng Thân Thiết bao gồm các cài đặt về điểm thưởng và làm tròn điểm trên các đơn vị sản phẩm, tiền tệ và đơn hàng và cho phép tạo ra các phần thưởng hoặc chiết khấu từ quỹ Điểm thưởng cho khách hàng

   * Điểm thưởng: Khách hàng sẽ được nhận điểm thưởng mỗi sản phẩm phù hơp với những sản phẩm đã được khai báo cho chương trình.
   * Quà tặng: Quà tặng có thể là giảm giá, quà tặng hoặc là sản phẩm

     * Tên: Một định danh nội bộ cho quà tặng
     * Số điểm tối thiểu: Số điểm thấp nhất mà khách hàng cần có để đạt được phần thưởng
     * Chi phí điểm thưởng: Số điểm giảm đi mỗi lần khách hàng đổi quà tặng

   * Chương trình khách hàng thân thiết: bạn có thể tạo ra các chương trình dựa trên sản phẩm, số lượng sản phẩm, số lượng đơn đặt hàng,..

     * Điểm trên mỗi đơn vị tiền: Số lượng điểm khách hàng nhận được trên số lượng tiền đã mua. *Ví dụ: khách hàng có thể nhận được một điểm mỗi đô la mà họ thanh toán.*
     * Điểm trên mỗi sản phẩm: Số lượng điểm khách hàng nhận được dựa trên số sản phẩm đã mua. *Ví dụ: Khách hàng có thể  nhận được X điểm khi mua sản phẩm Y*
     * Điểm trên mỗi đơn hàng: Số lượng điểm khách hàng nhận được cho mỗi đơn hàng. *Ví dụ: Khách hàng có thể nhận 2 điểm khi họ chỉ mua or 1 điểm khi mua từ điểm bán hàng của bạn.*
     * Phần thưởng: Phần thưởng cho khách hàng có thể là quà tặng hoặc giảm giá, giá trị của phần thưởng phụ thuộc vào số điểm khách hàng đã đổi.

#. Lập các quy tắc thay đổi cách nhận Điểm thưởng cho các sản phẩm hay nhóm sản phẩm đặc thù
#. Báo cáo và thống kê điểm thưởng với thước đo khác nhau theo các loại hình hiển thị khác nhau như dạng bảng, biểu đồ, đồ thị,...
#. Quản lý Chương trình Khách hàng Thân thiết và gán cho đội Bán Hàng theo yêu cầu mong muốn
#. Điều chỉnh điểm thủ công và làm tròn điểm thưởng
#. Thiết kế và nâng cấp tự động cấp độ khách hàng dựa trên số điểm thưởng tối thiểu của họ

   * Các mức khách hàng: cho phép bạn khai báo nhiều mức khách hàng *(Ví dụ: Khách hàng bạc, Khách hàng vàng, v.v.)*. Mỗi mức khách hàng sẽ có một hạn mức để được thăng hạng một cách tự động
   * Danh sách giá đối với thứ hạng khách: Cho phép đồng bộ danh sách giá đối với thứ hạng khách và danh sách giá đối với đối tác

#. Có thể sử dụng cho các ứng dụng khác để mở rộng

Chú ý
-----
Ứng dụng này được thiết kế như là một cơ sở cho các mô đun khác mở rộng. Ví du: Loyalty for PoS, Loyalty for Sales, Loyalty for eCommerce. Không có những mô đun kế thừa trên, mô đun này không có tác dụng.
Dưới đây là những ứng dụng tham khảo hiện tại:

* to_loyalty_sales: https://viindoo.com/apps/app/13.0/to_loyalty_sales (yêu cầu ứng dụng Quản lý bán hàng)
* to_loyalty_pos: https://viindoo.com/apps/app/13.0/to_loyalty_pos (yêu cầu ứng dụng Điểm bán hàng)

Ấn bản được hỗ trợ
==================
Ấn bản Community

""",
    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'sales_team'],
    # always loaded
    'data': [
        'data/module_data.xml',
        'security/loyalty_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/crm_team_views.xml',
        'views/loyalty_reward_views.xml',
        'views/loyalty_rule_views.xml',
        'views/loyalty_program_views.xml',
        'views/customer_level_views.xml',
        'views/loyalty_point_views.xml',
        'views/res_partner_views.xml',
        'views/loyalty_point_report.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
