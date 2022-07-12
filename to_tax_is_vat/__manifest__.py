{
    'name': "Tax Is VAT",
    'name_vi_VN': "Thuế GTGT",

    'summary': """Add VAT indicator on tax groups and taxes""",
    'summary_vi_VN': """Đánh dấu là thuế GTGT trên nhóm thuế và các loại thuế""",

    'description': """
Key Features
============
In some cases, we need to know if a tax is a value added tax. This module adds new field 'Is VAT' to the model ```account.tax.group``` and the model ```account.tax``` for that purpose

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng
=========
Trong một số trường hợp, chúng ta cần biết thuế có phải là thuế giá trị gia tăng hay không. Mô-đun này thêm trường mới 'Là thuế GTGT' vào mô hình ```account.tax.group``` và mô hình ```account.tax``` cho mục đích đó

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting',
    'version': '0.1.0',
    'depends': ['account'],
    'data': [
        'views/account_tax_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
