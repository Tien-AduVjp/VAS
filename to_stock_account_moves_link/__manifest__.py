{
    'name': "Stock Move & Account Move Links",
    'name_vi_VN': "Liên kết Dịch chuyển kho và Bút toán kế toán ",
    'summary': """
Porvides link between stock moves and account moves""",
    'summary_vi_VN': """
Cung cấp liên kết giữa dịch chuyển kho và bút toán kế toán""",
    'description': """
What it does
============
* Odoo does not provide any link between stock moves and their corresponding accounting moves (when real/fifo costing method is activated). This module was developed to fix such the issues.

Key Features
============
1. User Interfaces improvement for better tracking:

   * Inventory:

     * The corresponding Journal Items and Journal Entry are visible on the Stock Transfer form views to the users who have accountant's access rights
     * The corresponding Journal Items are visible on the Stock Move form views to the users who have accountant's access rights

   * Accounting:

     * Journal Item form view has information on its corresponding source invoice or source stock moves/transfers
     * Journal Entry form view has information on its source stock transfer

2. Technical Information

   * Journal Item's new relation fields

     * Invoice Line: the source invoice line from which the journal item was created
     * Stock Move: the source stock move from which the journal item was created
     * Stock Picking: the related source stock picking (aka stock transfer)

   * Journal Entry: Now has relation with the source stock picking/transfer to give accountants a better track on the entry.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Odoo không cung cấp bất kỳ liên kết nào giữa dịch chuyển kho và các phát sinh kế toán tương ứng của họ (khi phương thức tính giá thực/ fifo được đính hoạt). Module này được phát triển để khắc phục các vấn đề như vậy.

Tính năng nổi bật
=================

1. Cải thiện giao diện người dùng để theo dõi tốt hơn:

   * Kiểm kho:

     * Các phát sinh kế toán và bút toán sổ nhật ký tương ứng được hiển thị trên chế độ xem biểu mẫu dịch chuyển kho để người dùng có quyền truy cập của kế toán
     * Các phát sinh kế toán tương ứng trên chế độ xem biểu mẫu dịch chuyển kho để người dùng có quyền truy cập của kế toán

   * Kế toán:

     * Chế độ xem biểu mẫu của phát sinh kế toán có thông tin về hóa đơn gốc hoặc dịch chuyển kho nguồn tương ứng của nó.
     * Chế độ xem biểu mẫu của bút toán sổ nhật ký có thông tin về dịch chuyển kho nguồn của nó.

2. Thông tin kỹ thuật

   * Các trường mới của phát sinh kế toán

     * Dịch chuyển kho: Dịch chuyển kho nguồn từ chỗ mà phát sinh kế toán đã được tạo.
     * Giao nhận: Giao nhận kho nguồn liên quan (còn được gọi là dịch chuyển kho)

   * Bút toán sổ nhật ký: Bây giờ có liên quan đến việc giao nhận/dịch chuyển kho nguồn để cung cấp cho kế toán theo dõi tốt hơn về bút toán.

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
    'category': 'Technical Settings',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['stock_account'],

    # always loaded
    'data': [
        'views/account_move_line_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'installable': True,
    'auto_install': True,
    'application': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
