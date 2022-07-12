# -*- coding: utf-8 -*-
{
    'name': "HR Recruitment Website Editor",
    'name_vi_VN': "Sửa bài đăng tuyển dụng nhân sự trên Website",

    'summary': """
Allow Website Editors Edit Recruitment post on Website""",

    'summary_vi_VN': """
Cho phép Editors chỉnh sửa bài tuyển nhân sự trên Website được tạo bởi HR.
    	""",

    'description': """
What it does
============
* This module with bring you 2 setting options for helping Website / Editor and Designer have ability to edit HR's Recruitment Post.
* First option is for Website, it will allow Website / Editors edit HR Job on specific Website, you can find it in Website Setting.
* For example, Website 1 turn this on and Website 2 don't, Website / Editor and Designer can edit HR's Recruitment Post in Website 1, but they can't edit post in Website 2.
* Second is for Company, if turn on, it will allow Website Editors edit HR Job base on Company.
* If you want for Website, you can easily find it in Website Setting, and it name 'Website Editors Edit HR Post For Website'.
* If you want for Company, find it in Recruitment at Job Posting.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
* Module này tạo thêm 2 tùy chọn setting giúp Web cho Website / Editor and Designer có thể sửa bài đăng tuyển của HR trên website.
* Nếu chọn cho Website thì sẽ sẽ cho phép Website / Editor and Designer có thể sửa ở Website cụ thể dựa vào setting.
* Ví dụ, Website 1 được bật và Website 2 thì không, Website / Editor and Designer chỉ có thể sửa bài đăng ở Website 1, còn ở Website 2 thì không.
* Lựa chọn thứ 2 là cho phép sửa dựa trên company.
* Nếu muốn bật cho Website, hãy tìm ở Website Setting, có tên là 'Website Editors Edit HR Post For Website'.
* Nếu muốn bật cho company, hãy tìm ở Recruitment Setting ở mục Job Posting, có tên là 'Website Editors Edit HR Post For Company'.

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

    'category': 'Human Resources',
    'version': '0.1.0',
    # any module necessary for this one to work correctly
    'depends': ['website_hr_recruitment'],

    # always loaded
    'data': [
        'views/hr_recruitment_view.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
