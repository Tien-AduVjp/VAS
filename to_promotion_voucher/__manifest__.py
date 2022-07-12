{
    'name': 'Promotion / Gift Vouchers',
    'name_vi_VN': "Khuyến mại & Quà tặng",
    'version': '1.1.2',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'summary': 'Issue promotion vouchers then sell or give away to your customers',
    'summary_vi_VN': "Phát hành phiếu khuyến mãi sau đó bán hoặc tặng cho khách hàng của bạn",
    'sequence': 30,
    'category': 'Sales',
    'description': """
What it does
============

Built as a solid platform for other applications to extend, this application, in combination with its inheritance (other apps that extend this app), can help you:

* issue gift / promotion vouchers
* handle gift / promotion vouchers as storable products so that you can move them around locations within your company (e.g. move to retail shops after issuing)
* sell or give vouchers to your customers so that they can buy your goods and services, then pay you with the vouchers they have
* locate and track any voucher you have issued
* print voucher labels which contain the barcode for voucher identification using barcode scanner
* A voucher comes with a credit. For example,

    * you can sell a $500 voucher at the price of $300. When the customer pay you, she or he has full credit of $500
    * You can also give away $1000 voucher (aka selling at zero price). When the customer pay you, she or he has full credit of $1000

Key features
============

* Unlimited Voucher Types to categorize your vouchers with multiple promotion policies. Each type will be considered as master data for the vouchers in this type and consists of the following information

    * Name: the name of the voucher type. It could be something like "$100 Voucher", "$300 Voucher", "$1000 Voucher for Christmas 2018"
    * Voucher Value: the amount of credit you give to the vouchers of this type for payment by those vouchers
    * Voucher Profit Account: for accounting integration. When customers make payment using a promotion voucher of this type's,
      the profit (if any) created by the voucher credit will be encoded into this account. If None is set, the income account
      set on the voucher product will be used.
    * Voucher Loss Account: for accounting integration. When customers make payment using a promotion voucher of this type, the loss
      (if any) created by the voucher credit will be encoded into this account. If None is set, the expense account set on the
      voucher's corresponding product will be used.
    * Account Journal: the accounting journal for encoding entries regarding to promotion vouchers
    * Payable Once: is a boolean field to indicate if this type's vouchers could only be used for one-time payment even though they still
      have remaining credit
    * Valid Duration: is a number of days counted from issue date of a voucher with this type to its expiration date

* Issue a batch of vouchers in the same type.

    * Select a product that presents the voucher type
    * Input the quantity you want to issue
    * Hit Confirm button
    * Move the vouchers to your shops/stores to sell, distribute them

* A Voucher associated with a storable product through a unique serial number for tracking. Hence, it has the following

    * It can be sold as a normal product
    * It can be stocked as a normal storable product so that

        * you can manage your issued vouchers in several stores/shops
        * you can also do inventory for such the vouchers
        * you can also encoding voucher issue cost

    * It can be moved between your locations, e.g. from offices to stores, from a store to another.
    * It has unique serial number. Actually, it uses the native serial tracking feature offered by Odoo.
      You will have all traceability (up/down) information of a voucher

* Print Voucher Label

    * Voucher Label is a print version of a voucher where it contains voucher logistics serial and voucher barcode
    * When you sell voucher at Point of Sales, barcode will help you to identify the voucher
    * When you want to track / validate a voucher, logistic serial will help

* Multi-company is supported

    * In a multi-company environment, the application is smart enough to encode into the right account of the corresponding company

* Built as a solid platform for other application to extend. Please check out some of the applications that extends this:

    * Promotion Voucher - Accounting Payment (to_promotion_voucher_account_payment): https://viindoo.com/apps/app/13.0/to_promotion_voucher_account_payment
    * Promotion Vouchers for Point of Sales (to_promotion_voucher_pos): https://viindoo.com/apps/app/13.0/to_promotion_voucher_pos
    * Promotion Vouchers - Sales Management Integration (to_promotion_voucher_sale)
    * Promotion Voucher - Goods Return in Point of Sales (to_promotion_voucher_pos_return): https://viindoo.com/apps/app/13.0/to_promotion_voucher_pos_return
    * etc

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tổng quan
=========
Được xây dựng như một nền tảng để các module khác phát triển và mở rộng tính năng, Module này kết hợp với các module kế thừa, có thể giúp khách hàng:

* Phát hành phiếu quà tặng / khuyến mãi
* Xử lý các phiếu quà tặng / khuyến mãi dưới dạng các sản phẩm lưu trữ để bạn có thể dịch chuyển các voucher giữa các địa điểm trong công ty (ví dụ: chuyển đến các cửa hàng bán lẻ sau khi phát hành)
* Bán hoặc tặng voucher cho khách hàng để họ có thể mua sản phẩm dịch vụ của mình bằng các voucher đó
* Theo dõi các voucher đã phát hành
* Hỗ trợ in voucher có mã barcode
* Một chứng từ đi kèm với một tín dụng. Ví dụ:

    * Bạn có thể bán một phiếu mua hàng $ 500 ở mức giá $ 300. Khi khách hàng thanh toán cho bạn, họ có đầy đủ tín dụng là 500 đô la
    * Bạn cũng có thể tặng phiếu mua hàng trị giá $ 1000 (hay còn gọi là bán với giá bằng 0). Khi khách hàng thanh toán cho bạn, họ có đầy đủ tín dụng là $ 1000

Tính năng nổi bật
=================
* Không giới hạn các kiểu voucher để phân kiểu ứng với nhiều chính sách khuyến mãi. Mỗi kiểu voucher sẽ bao gồm các thông tin:

    * Name: tên của voucher. Ví dụ "Phiếu mua hàng $ 100", "Phiếu mua hàng $ 300", "Phiếu mua hàng $ 1000 cho Giáng sinh 2018"
    * Giá trị voucher: số tiền tín dụng bạn cấp cho các kiểu voucher thuộc kiểu này khi thanh toán
    * Tài khoản lợi nhuận voucher: để hợp nhất kế toán. Khi khách hàng thanh toán bằng voucher khuyến mãi kiểu này, lợi nhuận (nếu có) do tín dụng voucher tạo ra sẽ được hạch toán vào tài khoản này. Nếu Không được thiết lập, tài khoản doanh thu của sản phẩm ứng với voucher sẽ được sử dụng
    * Tài khoản lỗ Voucher: để hợp nhất kế toán. Khi khách hàng thanh toán bằng voucher khuyến mãi kiểu này, khoản lỗ (nếu có) do tín dụng voucher tạo ra sẽ được hạch toán vào tài khoản này. Nếu Không được thiết lập, tài khoản chi phí của sản phẩm ứng với voucher sẽ được sử dụng
    * Nhật ký tài khoản: nhật ký kế toán để hạch toán các bút toán liên quan đến phiếu khuyến mãi
    * Thanh toán một lần: nếu chọn, kiểu voucher này chỉ được sử dụng 1 lần dù vẫn còn tín dụng
    * Thời hạn hiệu lực: là số ngày được tính từ ngày phát hành kiểu voucher này đến ngày hết hạn

* Phát hành nhiều số lượng voucher cùng kiểu

    * Chọn sản phẩm đại diện cho kiểu voucher
    * Chọn số lượng voucher phát hành
    * Xác nhận
    * Dịch chuyển voucher đến cửa hàng của bạn để phân phối chung

* Một voucher được coi như một sản phẩm tồn kho, có gán lô sê ri duy nhất. Do đó, một voucher có thể:

    * Có thể bán như một sản phẩm bình thường
    * Có thể lưu kho để quản lý, kiểm kê và hạch toán chi phí
    * Cho phép dịch chuyển các voucher qua từng địa điểm, ví dụ từ văn phòng đến cửa hàng, từ cửa hàng này đến cửa hàng khác
    * Được gán Sê-ri duy nhất để phục vụ truy xuất nguồn gốc

* Hỗ trợ in nhãn voucher

    * Nhãn voucher có chưa các thông tin về Sê-ri và mã của voucher
    * Có thể phân biệt các voucher bằng mã vạch khi bán chúng tại các Điểm bán lẻ
    * Sê-ri có thể giúp truy vết hoặc xác nhận một voucher

* Hỗ trợ sử dụng trong môi trường đa công ty

    * Trong môi trường đa công ty, phần mềm hỗ trợ hạch toán vào các tài khoản của công ty tương ứng

* Được xây dựng như một nền tảng vững chắc cho các ứng dụng khác mở rộng. Vui lòng kiểm tra một số ứng dụng mở rộng điều này:

    * Phiếu khuyến mãi - Thanh toán kế toán (to_promotion_voucher_account_payment): https://viindoo.com/apps/app/13.0/to_promotion_voucher_account_payment
    * Phiếu thưởng khuyến mãi cho Điểm bán hàng (to_promotion_voucher_pos): https://viindoo.com/apps/app/13.0/to_promotion_voucher_pos
    * Phiếu thưởng khuyến mãi - Tích hợp quản lý bán hàng (to_promotion_voucher_sale)
    * Phiếu khuyến mãi - Trả hàng tại điểm bán hàng (to_promotion_voucher_pos_return): https://viindoo.com/apps/app/13.0/to_promotion_voucher_pos_return
    
Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'depends': ['stock_account', 'to_base', 'to_location_warehouse'],
    'data': [
        'data/scheduler_data.xml',
        'data/res_config_settings.xml',
        'data/voucher_type_data.xml',
        'data/pagerformat_data.xml',
        'data/product_category_data.xml',
        'data/sequence.xml',
        'data/res_company_data.xml',
        'data/account_data.xml',
        'data/stock_warehouse_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/stock_move_line_views.xml',
        'views/stock_production_lot_views.xml',
        'views/account_chart_template_views.xml',
        'views/product_view.xml',
        'views/voucher_view.xml',
        'views/voucher_type_view.xml',
        'views/voucher_product_view.xml',
        'views/account_journal_view.xml',
        'views/voucher_issue_order_view.xml',
        'views/voucher_move_order_view.xml',
        'views/voucher_give_order_view.xml',
        'views/voucher_report.xml',
        'views/account_move_line_views.xml',
        'views/stock_warehouse_view.xml',
        'views/res_config_view.xml',
        'report/voucher_barcode_templates.xml',
        'report/voucher_barcode_reports.xml',
        'wizard/extend_expired_vouchers_view.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
