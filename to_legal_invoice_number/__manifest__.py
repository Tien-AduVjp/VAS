{
    'name': "Legal Invoice Number",
    'name_vi_VN': "Số hóa đơn giá trị gia tăng",

    'summary': """
An additional number for invoice""",

    'summary_vi_VN': """
Một số bổ sung cho hóa đơn
        """,

    'description': """
Key Features
============
#. A new field 'Legal Number' has been added to the invoice model to allow users to

   * Input an additional invoice number for legal purpose
   * Search invoice by legal number

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
#. Một trường mới 'Số Hoá đơn GTGT' đã được thêm vào hóa đơn để cho phép người dùng

   * Nhập bổ sung một mã số hoá đơn giá trị gia tăng theo luật định
   * Tìm kiếm hóa đơn theo số hóa đơn giá trị gia tăng

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Accounting',
    'version': '0.1.0',
    'depends': ['account'],
    'data': [
        'data/ir_action_server_data.xml',
        'views/account_move_views.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': False,
    'auto_install': False,
}
