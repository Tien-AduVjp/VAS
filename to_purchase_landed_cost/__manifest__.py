{
    'name': "Purchase and Track Landed Costs",
    'name_vi_VN': "Mua hàng và theo dõi chi phí về kho",

    'summary': """
Improve Landed Costs with Purchase""",
    'summary_vi_VN': """
Cải tiến chi phí về kho với Mua Hàng""",

    'description': """
Upon validation of a Purchase Order, automaticaly create other Purchase Orders for landed costs that would be allocated to the products
of the first Purchase Order.

Keep track the the landed costs (the amount, where they come from, why you have them, etc)

The problems
============

By default, Odoo's Stock Landed Cost application just provides a mean to allocate landed costs to stockable products without any means
for tracking or manage landed cost purchase. For example, when you purchase product A, you may also need to purchase transportation
service product B for another vendor. What would you encode such the information in Odoo? You probably:

1. Create 2 purchase orders
2. Receive the product A
3. Open the second PO to get the cost of the transportation service
4. Create a landed cost to allocate the cost of the transportation service to the product A

After, when you look into the list of thousand lines of landed costs, how you know if the costs are relevant?
Is there anything wrong there? How to know if anything wrong there?

The Solution
============

This application was developed to solve the above mention problems by provide lots of must-have features to ensure that

* you can have some landed cost PO generated automatically when you confirm a PO that may require landed costs to be purchased
* you can create stock landed costs from a landed cost invoice
* everything related to landed costs is trackable. I.e. Landed Cost Adjustments, Landed Costs Purchases, Landed Costs Invoices, original purchase orders, landed costs' account journal items, etc

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Sau khi xác thực đơn mua, Tự động tạo các đơn mua khác cho chi phí về kho sẽ được phân bổ cho các sản phẩm của đơn mua đầu tiên.
Theo dõi các chi phí về kho (Số tiền, chúng đến từ đâu, tại sao bạn có chúng,...)

Những vấn đề
============
Theo mặc định, ứng dụng chi phí về kho của Odoo chỉ cung cấp một phương pháp phân bổ chi phí về kho cho các sản phẩm có thể tồn kho mà không có bất kỳ những phương pháp khác
để theo dõi hoặc quản lý chi phí về kho của đơn mua.
Ví dụ, Khi bạn mua sản phẩm A, bạn có thể cũng cần mua dịch vụ vận chuyển B cho một nhà cung cấp khác.
Bạn sẽ mã hóa thông tin như vậy trong odoo như nào? : Bạn có thể:

1. Tạo 2 đơn mua
2. Nhận sản phẩm A
3. Mở đơn mua thứ 2 để nhận chi phí dịch vụ vận chuyển
4. Tạo một chi phí về kho để phân bổ cho dịch vụ vận chuyển của sản phẩm A

Sau đó, khi bạn nhìn vào danh sách hàng nghìn dòng của chi phí về kho, làm thế nào bạn biết các chi phí có liên quan đến nhau?
Có gì sai ở đó? làm thế nào để biết nếu có bất kì sai ở đó?

Giải pháp
=========

Ứng dụng này được phát triển để giải quyết các vấn đề cập phía trên bằng cách cung cấp nhiều tính năng phải có để đảm bảo rằng:

* Bạn có thể có một số chi phí về kho của đơn mua được tạo tự động khi bạn xác nhận một đơn mua có thể yêu cầu chi phí về kho khi mua
* Bạn có thể tạo chi phí về kho từ hóa đơn phí về kho
* Mọi thứ liên quan đến chi phí về kho đều có thể theo dõi.  Điều chỉnh chi phí về kho, Đơn mua chi phí về kho, Hóa đơn chi phí về kho, đơn mua ban đầu, phát sinh kế toán tài khoản của chi phí về kho,...

Ấn bản hỗ trợ
=============
1. Ấn bản cộng đồng
2. Ấn bản doanh nghiệp

    """,

    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchases',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_landed_costs', 'purchase', 'to_stock_account_moves_link'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_line_views.xml',
        'views/account_invoice_views.xml',
        'views/stock_landed_cost_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
