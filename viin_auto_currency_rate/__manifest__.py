{
    'name': "Bank Currency Rates Update",
    'name_vi_VN': "Tự Động Cập Nhật Tỷ Giá Tiền Tệ Theo Ngân Hàng",

    'summary': """
Automatic update currency rates by bank
""",
    'summary_vi_VN': """
Tự động cập nhật tỷ giá tiền tệ theo ngân hàng
""",

    'description': """
What it does
============
* For companies that use multi-currency, users need to manually input the exchange rate every day or every time there is a rate change.
* This takes a long time and could cause errors if users forget to update.
* This module is the base module for others to get automatic exchange rates from different banks every time there is a rate change.

Key Features
============
- Automatic rates updates of the actives currencies
- Configurable updates intervals
- Allow manual updates of selected currencies

Note:
-----
Again, this module provides a solid platform for other modules to extend. The module means nothing when staying alone.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,
    'description_vi_VN': """
Mô tả
=====
* Đối với các công ty sử dụng đa tiền tệ, người dùng phải nhập thủ công tỷ giá giữa đồng ngoại tệ - đồng cơ sở hàng ngày hoặc mỗi khi có sự thay đổi về tỷ giá. 
* Việc này vừa mất nhiều thời gian vừa có nguy cơ sai sót nếu người dùng quên cập nhật.
* Mô-đun này là cơ sở cho những mô-đun khác để lấy tỷ giá tự động từ các ngân hàng khác nhau mỗi khi có thay đổi.

Tính năng nổi bật
=================
- Tự động cập nhật tỷ giá của các loại tiền tệ đang kích hoạt
- Cho phép cấu hình thời gian cập nhật định kỳ (VD: hàng ngày, hàng tuần)
- Cho phép cập nhật thủ công các đơn vị tiền tệ đã chọn

Lưu ý:
------
Nhắc lại, module này xây dụng để cho các module khác kế thừa. Và nó không thể hoạt động độc lập.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise


    """,
    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['to_bank_currency_rate'],

    # always loaded
    'data': [
        'data/scheduler_data.xml',
        'view/res_bank_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
