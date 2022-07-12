{
    'name': "Stock Barcode",
    'name_vi_VN': 'Tích hợp Mã vạch với Kho vận',
    'old_technical_name': 'stock_barcode',
    'summary': "Add barcode scanning facilities to support inventory and stock operations",
    'summary_vi_VN': "Tích hợp quét mã vạch để hỗ trợ các hoạt động trong kho",
    'description': """
What it does
============
This module helps to define inventory and stock operations with the barcodes, then the inventory user can easily use the barcode scanner to search, fill the data
faster to save time and improve work efficiency.

Key Features
============
Allowing barcode scanning of products and warehouse operations as follows:

* Products'barcodes in Lots and Serial Numbers
* Warehouse operations includes:

  * Search for Receipt or Delivery orders: For example, a receipt order with a printable barcode, when the inventory user scans that barcode,
    the system will display the corresponding receipt order. The inventory user continues to scan the barcode of the products and confirm the quantity to receive the product(s).
    Same with other inventory operations.
  * Create inventory transfer(s) in each inventory location: if you have set up barcodes for operations in each inventory location (for example: YourCompany: Receipt,
    Branch: Internal transfer, etc.). When scanning that barcode, the system will automatically generate the corresponding inventory transfer order. Then, inventory user
    continues to scan the product barcode to fill the corresponding product and quantity.
  * Replace actions on transfer orders (e.g. Save, Discard. Edit, Print delivery slip, etc.)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
Mô-đun này giúp mã hóa các sản phẩm và hoạt động trong kho bằng hệ thống mã vạch (barcode), nhân viên kho có thể dễ dàng sử dụng máy quét để tìm kiếm, thao tác nhanh hơn trên hệ thống
giúp tiết kiệm thời gian và làm việc hiệu quả hơn.

Tính năng nổi bật
=================
Cho phép quét mã vạch (barcode) các sản phẩm và hoạt động trong kho như sau:

* Mã vạch sản phẩm theo số lô, số series
* Các hoạt động trong kho bao gồm:

  * Tìm kiếm các phiếu nhập, xuất kho. Ví dụ: trên phiếu nhập kho có in sẵn một mã vạch, khi nhân viên quét mã vạch đó, hệ thống sẽ hiển thị đúng phiếu nhập kho đó.
    Nhân viên tiếp tục quét mã vạch các sản phẩm và xác nhận số lượng để nhập kho. Tương tự với hoạt động xuất kho.
  * Tạo các phiếu dịch chuyển theo từng địa điểm kho: nếu đã thiết lập mã vạch cho các hoạt động trong từng địa điểm kho (ví dụ: Kho tổng: Nhập hàng, Kho chi nhánh: Dịch chuyển nội bộ v.v)
    khi quét mã vạch đó, hệ thống sẽ tự động tạo phiếu dịch chuyển tương ứng. Từ đó, nhân viên kho tiếp tục quét mã vạch sản phẩm để nhập sản phẩm và số lượng tương ứng.
  * Thay thế các hành động trên các phiếu dịch chuyển (ví dụ: Lưu, Hủy. Chỉnh sửa, In phiếu giao hàng v.v)

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'category': 'Warehouse',
    'version': '1.1',
    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com/',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'depends': ['barcodes', 'to_enterprise_marks_stock'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_barcode_lot_view.xml',
        'wizard/stock_track_confirmation_views.xml',
        'views/assets.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_barcode_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_scrap_views.xml',
    ],
    'qweb': [
        "static/src/xml/stock_barcode.xml",
    ],
    'demo': [
        'data/demo.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
