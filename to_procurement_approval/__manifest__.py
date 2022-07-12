{
    'name': "Procurement Approvals",
    'name_vi_VN': "Phê duyệt mua sắm",
    'summary': """
Employees create procurement approval request for products and submit to managers.
""",

    'summary_vi_VN': """
Nhân viên tạo yêu cầu phê duyệt mua sắm cho một hay nhiều Sản phẩm và trình lên người quản lý.
    	""",

    'description': """
Key Features
============

1. Employees create a request procurement for one or more products with

    * a desired quantity
    * a preferred warehouse
    * at a desired date

2. Manager approves or refuses the request
3. Before approval, if the products is not service type, managers can select a preferred routes
4. Once approved,for non-service type products Odoo will automate the supply process according to the predefined or selected routes
   (either get from stock or manufacture or propose a draft purchase order, etc). If the product is a service type, Odoo will create a PO for that product

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Tính năng chính
===============

1. Nhân viên tạo một yêu cầu phê duyệt mua sắm cho một hay nhiều sản phẩm với:

   * số lượng mong muốn
   * cho kho hàng mong muốn
   * vào một ngày mong muốn

2. Người quản lý có thể Duyệt hoặc Từ chối yêu cầu.
3. Trước khi duyệt, nếu sản phẩm không phải kiểu dịch vụ người quản lý có thể chọn một tuyến cung ứng phù hợp hoặc để trống để sử dụng tuyến cung ứng mặc định cho sản phẩm
4. Một khi được duyệt, đối với sản phẩm không phải dịch vụ Odoo sẽ tự động tạo các hoạt động cung ứng phù hợp để đáp ứng theo nhu cầu (vd: tạo dịch chuyển hàng hoá liên kho,
   tạo lệnh sản xuất để đáp ứng, đề xuất một đơn mua hàng dự thảo. Nếu sản phẩm là dịch vụ, Odoo sẽ tạo ra PO cho sản phẩm đó

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Warehouse',
    'version': '0.1',
    'depends': ['to_approvals','stock','purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
        'views/procurement_group_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
