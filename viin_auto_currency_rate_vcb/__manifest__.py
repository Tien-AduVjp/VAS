{
    'name': "Automatic Currency Rates Update VietcomBank",
    'name_vi_VN': 'Tự Động Cập Nhật Tỷ Giá Ngoại Tệ Ngân Hàng VietcomBank',
    'summary': """
Automatically update the currency rates by VietcomBank""",
    'summary_vi_VN': """
Tự động cập nhật tỷ giá ngoại tệ theo ngân hàng VietcomBank""",
    'description': """
What it does
============
This is the legacy module of '''viin_auto_currency_rate''', it enables automatic updates exchange rates from VCB (Joint Stock Commercial Bank for Foreign Trade of Vietnam) in the Accounting module.

Key Features
============
- Automatic rates updates of the actives currencies according to the exchange rate at VCB
- Configurable updates intervals
- Allow manual updates of selected currencies

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
Là module kế thừa của module '''viin_auto_currency_rate''', cho phép tự động cập nhật định kỳ tỷ giá hối đoái từ ngân hàng Vietcombank trong phân hệ Kế toán.

Tính năng nổi bật
=================
- Tự động cập nhật tỷ giá của các loại tiền tệ đang kích hoạt theo đúng tỷ giá tại ngân hàng VCB
- Cho phép cấu hình thời gian cập nhật định kỳ (VD: hàng ngày, hàng tuần)
- Cho phép cập nhật thủ công các đơn vị tiền tệ đã chọn

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',

    'category': 'Accouting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_auto_currency_rate'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
