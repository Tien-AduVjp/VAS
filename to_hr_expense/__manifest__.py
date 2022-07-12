{
    'name': "Viin HR Expenses",
    'name_vi_VN': "Tùy chỉnh Chi Tiêu",

    'summary': """
Fine tunning for HR Expenses app for advanced features and better UX
    """,

    'summary_vi_VN': """
Tùy biến ứng dụng Chi tiêu Nhân sự để có các tính năng nâng cao và trải nghiệm người dùng tốt hơn
        """,

    'description': """
What it does
============
Allows you to customize some of the information when create expense

1. Allow to choose the vendor on the expense form
2. Allow to encode expense entries as vendor bills
3. Allow the user to choose taxes on expense declarations

Create link between account entries and hr expenses to easy trace expense account entry.

1. Allow group by expense on journal entries/items list view
2. Allow filter journal entries/items which are expense entries/items
3. Link journal entry to hr expense

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Cho phép bạn tùy chỉnh một số thông tin khi tạo chi tiêu

1. Cho phép chọn nhà cung cấp trên form chi tiêu
2. Cho phép ghi nhận các chi tiêu như là các hóa đơn nhà cung cấp
3. Cho phép người dùng có quyền chọn thuế

Cho phép liên kết các bút toán với chi tiêu để dễ dàng truy xuất nguồn gốc các bút toán chi tiêu

1. Cho phép nhóm theo chi tiêu trên danh sách bút toán và phát sinh bút toán
2. Cho phép lọc ra các bút toán/phát sinh liên quan đến chi tiêu
3. Liên kết bút toán với chi tiêu

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
    'category': 'Accounting/Expenses',
    'version': '0.3.4',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense', 'to_account_payment'],

    # always loaded
    'data': [
        'views/hr_expense_view.xml',
        'views/hr_expense_sheet_view.xml',
        'views/account_move_line.xml',
        'views/account_move.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 199.8,
    'currency': 'EUR',
    'license': 'OPL-1',
}
