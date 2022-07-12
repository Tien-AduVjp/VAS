{
    'name': "Warranty Management",
    'name_vi_VN': "Bảo hành",

    'summary': """
Manage product warranty policies and warranty claims.
""",

    'summary_vi_VN': """
Quản lý các chính sách bảo hành và quy trình yêu cầu bảo hành
""",

    'description': """
What it does
============
* This module manages product warranty policies & warranty claims and allows users to declare warranty policies applicable to each product.
* Warranty policies can be applied by the warranty period or product milestones.
* Allow users to manage the process of warranty claims: claim, investigate, confirm, refuse, finish.

Key Features
============
* Set up warranty policy on product form:

  * By timeline (24 months, 36 months, etc.)
  * By product operating milestone (1000 hours, 2000 km, etc.)

* Automatically calculate warranty expiration date
* Look up warranty information by lot/serial number:

  * Look up product information
  * Check warranty expiration date

* Integrate warranty with repair:

  * Create repair orders right on the warranty interface
  * Look up repair history of the warranty

* Create warranty analysis and report by many criteria: partner, product, warranty status, lot/serial number, etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """

Mô tả
=====
* Mô-đun này quản lý các chính sách bảo hành & quy trình yêu cầu bảo hành và cho phép khai báo các chính sách bảo hành áp dụng cho từng sản phẩm.
* Các chính sách bảo hành có thể áp dụng theo khoảng thời gian bảo hành hoặc các mốc hoạt động của sản phẩm.
* Cho phép quản lý quy trình yêu cầu bảo hành: Tạo mới yêu cầu, đánh giá tình trạng, xác nhận hoặc từ chối bảo hành, hoàn thành bảo hành.

Tính năng nổi bật
=================
* Thiết lập chính sách bảo hành trên form sản phẩm:

  * Theo mốc thời gian (24 tháng, 36 tháng...)
  * Theo mốc hoạt động của sản phẩm (1000 giờ, 2000 km...)
  * Tự động tính toán ngày hết hạn bảo hành

* Tra cứu thông tin bảo hành theo số lô/sê-ri:
  * Tra cứu thông tin sản phẩm
  * Kiểm tra ngày hết hạn bảo hành

* Tích hợp bảo hành với sửa chữa:

  * Tạo lệnh sửa chữa ngay trên giao diện bảo hành
  * Tra cứu lịch sử sửa chữa của bảo hành

* Phân tích, báo cáo bảo hành theo nhiều tiêu chí: đối tác, sản phẩm, tình trạng bảo hành, số lô/sê-ri...

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
    'category': 'Warranty Management',
    'version': '0.1',
    'depends': ['product', 'to_product_milestone'],
    'old_technical_name': 'to_warrantee_management',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/root_menu.xml',
        'views/product_views.xml',
        'views/warranty_claim_views.xml',
        'views/warranty_policy_views.xml',
        'wizard/action_confirm_wizard_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 45.9,
    'subscription_price': 3.31,
    'currency': 'EUR',
    'license': 'OPL-1',
}
