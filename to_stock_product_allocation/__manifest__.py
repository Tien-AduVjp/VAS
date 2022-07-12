{
    'name': "Product Warehouses Distribution",
    'name_vi_VN': "Phân phối sản phẩm giữa các kho",

    'summary': """
Distributes products from a single warehouse across several warehouses
""",

    'summary_vi_VN': """
Phân bổ hàng hóa từ một kho tới nhiều kho khác 
        """,

    'description': """
What it does
============
* Allow employees to create stock allocation requests for products with desired quantities, source and destination warehouses and dates.
* Allow managers to approve or refuse the requests.

Key Features
============
* Employees submit a stock allocation request for one or more products with:

   * a desired quantity
   * a source warehouse
   * a destination warehouse
   * at a desired date

* Managers approve or refuse the request.
* Once approved, Odoo will find or create a new resupply route between the source warehouse and the destination warehouse then create appropriate transfers and assign them to allocate products accordingly.

Supported Editions
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Mô tả
=====
* Cho phép nhân viên tạo yêu cầu phân bổ kho cho sản phẩm với số lượng, kho nguồn, kho đích và thời gian mong muốn.
* Cho phép quản lý chấp thuận hoặc từ chối yêu cầu.

Tính năng nổi bật
=================
* Nhân viên sẽ tạo một yêu cầu phân bổ kho cho một hoặc nhiều sản phẩm: 

  * Số lượng mong muốn
  * Từ kho hàng mong muốn
  * Vào một ngày mong muốn
  * Đến kho hàng mong muốn

* Người quản lý có thể Duyệt hoặc Từ chối yêu cầu.
* Một khi được duyệt, Odoo sẽ dựa vào kho nguồn và các kho đích để tìm hoặc tự động tạo mới các tuyến cung ứng giữa các kho, sau đó thực hiện các hành động dịch chuyển phù hợp để phân phối hàng hóa.

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
    'version': '0.2',
    'depends': ['stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'security/ir.model.access.csv',
        'views/allocation_request_views.xml',
        'views/procurement_group_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
