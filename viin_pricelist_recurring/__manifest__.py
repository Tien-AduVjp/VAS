{
    'name': "Recurring Pricelist",
    'name_vi_VN': "Bảng giá định kỳ",

    'summary': """
Recurring Pricelist every month or year""",

    'summary_vi_VN': """
Bảng giá định kỳ theo tháng hoặc năm""",

    'description': """
Key Features
============
This module allows you to configure a recurring pricelist rule:

- Recurring period could be monthly or annually.
- If period is monthly, you can specify the day from and day to for every month.
- If period is annually, you can specify the day/month from and day/month to for every year.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition
    """,

    'description_vi_VN': """
Tính năng chính
===============
Mô-đun này cho phép bạn cấu hình một quy tắc bảng giá lặp lại định kỳ:

- Chu kỳ lặp lại có thể là hàng tháng hoặc hàng năm.
- Nếu chu kỳ là hàng tháng, bạn có thể chỉ định ngày bắt đầu và ngày kết thúc cho mỗi tháng.
- Nếu chu kỳ là hàng năm, bạn có thể chỉ định ngày/tháng bắt đầu và ngày/tháng kết thúc cho mỗi năm.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "apps.support@viindoo.com",
    'category': 'Sales',
    'version': '0.1.0',
    'depends': ['product'],
    'data': [
        'views/product_pricelist_item_view.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
