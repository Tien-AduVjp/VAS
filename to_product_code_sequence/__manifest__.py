{
    'name': "Auto Product Code Generation",
    'name_vi_VN': "Tự động tạo Mã Sản Phẩm",

    'summary': """
Automatic Product Code Generation on product creation
""",
    'summary_vi_VN': """
Tự động tạo Mã Sản Phẩm khi tạo mới Sản Phẩm""",

    'description': """
What it does
============
* Add new fields into the *Product Category*:

   * *Product Sequence*: to provide increment sequence for the product code
   * *Product Code Prefix*: that will be combined with the code generated by the sequence

* Automatically generate and update product codes (shown as *Internal Reference* in the interface) based on *Product Name* or the defined *Product Code Prefix* and *Product Sequence*

Key Features
============
* Define *Product Code Prefix* and *Product Sequence* (create new/ choose from the available list) in the *Product Category*
* Automatically generate product codes by combining the *Product Code Prefix* and *Product Sequence* - apply for multiple products and product variants at once
* Update old product codes according to the defined *Product Code Prefix* and *Product Sequence* by clicking *Update Product Code* in the *Action* dropdown menu
* **Demo video:** https://youtu.be/zuqgo5WUaJg

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Ứng dụng này thêm mới vào *Nhóm Sản Phẩm* các trường:

   * *Mã trình tự*: được đặt theo số thứ tự tăng dần
   * *Tiền tố mã sản phẩm*: được kết hợp đứng trước Mã trình tự của Sản phẩm

* Tự động tạo và cập nhật mã sản phẩm (hiển thị là *Mã nội bộ* trong giao diện) dựa trên việc kết hợp *Tên sản phẩm* hoặc *Tiền tố mã sản phẩm* cùng với *Mã trình tự* của sản phẩm

Tính năng nổi bật
=================
* Người dùng có thể định nghĩa *Tiền tố mã sản phẩm* và *Mã trình tự* (bằng cách tạo mới/ chọn trong danh sách có sẵn) trong *Nhóm Sản Phẩm*
* Tự động tạo mã sản phẩm bằng cách kết hợp *Tiền tố mã sản phẩm* và *Mã trình tự* - áp dụng cho nhiều sản phẩm và biến thể sản phẩm cùng một lúc
* Cập nhật mã sản phẩm cũ theo *Tiền tố mã sản phẩm* và *Mã trình tự* đã xác định, bằng cách nhấp vào *Cập nhật mã sản phẩm* trong mục *Hành động*
* **Video Hướng dẫn:** https://youtu.be/zuqgo5WUaJg

Ấn bản hỗ trợ
=============
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['product'],

    # always loaded
    'data': [
        'data/ir_sequence.xml',
        'data/ir_actions_server.xml',
        'views/product_category_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 45.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
