{
    'name': "Survey Time Limit",
    'name_vi_VN': "Giới hạn thời gian Survey",
    'summary': """
        Set CSRF token time by survey time limit""",
    'summary_vi_VN': """
        Thiết lập thời gian CSRF token theo thời gian của survey""",
    'description': """
Key Features
============
Without this module installed:

* The CSRF token is causing survey submissions to crash after 1h, because the token never seems to be refreshed. 
* It can even lead to blocking bugs, e.g. when the 1h expiration occurs in the middle of taking a survey exam, and the user is never able to post the answers that are only present in the state of the form they need to post.

With this module installed:

* If survey's time limit > 60 minutes, the CSRF tokens are based on the current time limit of survey, and automatically expire as soon as the survey done.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Tính năng nổi bật
=================
Nếu không cài đặt module này:

* Mã CSRF đang gây ra sự cố khi nộp bài khảo sát sau 1 giờ, vì mã CSRF không bao giờ được làm mới.
* Nó thậm chí có thể dẫn đến lỗi, ví dụ: khi hết 1 giờ xảy ra ở giữa thời gian thực hiện khảo sát và người dùng không bao giờ có thể nộp kết quả.

Với mô-đun này được cài đặt:

* Nếu giới hạn thời gian của khảo sát > 60 phút, thì mã CSRF dựa trên thời hạn giới hạn hiện tại của khảo sát và tự động hết hạn ngay sau khi khảo sát hết hạn.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,
    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Survey',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['survey'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/survey_templates.xml',
    ],
    'qweb': [
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
