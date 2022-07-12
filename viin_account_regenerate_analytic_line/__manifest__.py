{
    'name': 'Regenerate Account Analytic Lines',
    'name_vi_VN': 'Tạo lại Phát sinh Kế toán Quản trị',
    'version': '0.1.0',
    'category': 'Accounting',
    'summary': """Adjust Account Analytic Lines for Posted Journal Items""",
    'summary_vi_VN': """Điều chỉnh Phát sinh Kế toán Quản trị cho các Phát sinh Kế toán đã vào sổ""",
    'description': """
The problem
===========
By default, you cannot add or adjust analytic account for posted journal items, so you cannot regenerate analytic lines for them.

Solution
========
This module provides action menu on journal items form and tree views. You can select one or many journal items and click on this action menu.
When the popup was displayed, you should select analytic account, analytic tags then click confirm. The new analytic lines should be auto regenerated for the chosen journal items. 

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Vấn đề
======
Mặc định, khi bút toán đã vào sổ bạn sẽ không thể thêm hoặc điều chỉnh tài khoản quản trị cho các phát sinh, do đó bạn cũng không thể tạo lại các phát sinh kế toán quản trị cho chúng.

Giải pháp
=========
Mô-đun này cung cấp menu `Tạo lại Phát sinh Kế toán Quản trị` ở giao diện form và danh sách của phát sinh kế toán. Người dùng có thể chọn một hoặc nhiều phát sinh, sau đó bấm vào menu này.
Khi Popup được mở ra, người dùng chọn tài khoản kế toán quản trị, thẻ TK kế toán quản trị và bấm xác nhận. Hệ thống sẽ tự động tạo lại các phát sinh toán kế toán quản trị cho các phát sinh kế toán đã được chọn.

Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author' : 'Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',
    'depends': [
        'account',
    ],
    'data': [
        'wizard/account_analytic_lines_regenerate.xml',
        'views/account_move_views.xml',
        'views/account_move_line_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
