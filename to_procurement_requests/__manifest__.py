{
    'name': "Replenishment Requests",

    'summary': """
Employees create replenishment requests for products and submit to managers.
""",

    'summary_vi_VN': """
Nhân viên tạo Yêu cầu Tái Cung ứng cho một hay nhiều Sản phẩm và trình lên người quản lý.
    	""",

    'description': """
Key Features
============

1. Employees Submit a replenishment request for one or more products with

    * a desired quantity
    * a preferred warehouse
    * at a desired date
2. Manager approves or refuses the request
3. Before approval, managers can select a preferred routes
4. Once approved, Odoo will automate the supply process according to the predefined or selected routes
   (either get from stock or manufacture or propose a draft purchase order, etc)

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Tính năng chính
===============

1. Nhân viên gửi một Yêu cầu cung ứng cho một hay nhiều sản phẩm với:
   
   * số lượng mong muốn
   * cho kho hàng mong muốn
   * vào một ngày mong muốn
   
2. Người quản lý có thể Duyệt hoặc Từ chối yêu cầu.
3. Trước khi duyệt, người quản lý có thể chọn một tuyến cung ứng phù hợp hoặc để trống để sử dụng tuyến cung ứng mặt định cho sản phẩm
4. Một khi được duyệt, Odoo sẽ tự động tạo các hoạt động cung ứng phù hợp để đáp ứng theo nhu cầu (vd: tạo dịch chuyển hàng hoá liên kho,
   tạo lệnh sản xuất để đáp ứng, đề xuất một đơn mua hàng dự thảo (hoặc trộn vào đơn mua dự thảo sẵn có của cùng nhà cung cấp).

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Hidden',
    'version': '0.2',
    'depends': ['stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/root_menu.xml',
        'views/replenishment_request_views.xml',
        'views/procurement_group_views.xml',
    ],
    'images' : [
    	# 'static/description/main_screenshot.png'
    	],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'subscription_price': 4.97,
    'currency': 'EUR',
    'license': 'OPL-1',
}
