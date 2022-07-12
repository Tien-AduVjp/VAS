{
    'name': "Company Hotline",
    'name_vi_VN': "Đường dây nóng của công ty",

    'summary': """
Hotline for partners and the company
        """,
    'summary_vi_VN': """
Đường dây nóng của đối tác và công ty""",
    'description': """

What it does
============
Add Hotline to the partner information form when the contact is in company type

Key Features
============
* Store a partner's hotline if any
* Search a partner by typing hotline in the search bar
* Do not apply for partners in indivisual type

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,
        'description_vi_VN': """

Mô tả
=====
Hiển thị thêm trường Đường dây nóng trong bảng thông tin của đối tác, nếu đối tác ở dạng công ty

Tính năng nổi bật
=================
* Cho phép lưu trữ thông tin đường dây nóng của đối tác (nếu có)
* Cho phép tìm kiếm đối tác bằng thông tin đường dây nóng tại thanh tìm kiếm
* Không áp dụng khi đối tác ở dạng cá nhân

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Company',
    'version': '1.0.1',
    'depends': ['base'],

    'data': [
        'views/company_hotline.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
