{
    'name': "Survey Exam",
    'name_vi_VN': "Tạo đề thi sử dụng khảo sát",

    'summary': """
Create exam using survey.
        """,

    'summary_vi_VN': """
Tích hợp với Khảo sát để tạo đề thi.
    	""",

    'description': """
Key Features
============
This module allow:

* Create questions bank
* Generate survey from questions bank
* Generate questions bank from suvey questions

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng nổi bật
=================
Module này cho phép:

* Tạo ngân hàng câu hỏi
* Tạo khảo sát từ ngân hàng câu hỏi
* Cho phép tạo ngân hàng câu hỏi từ các câu hỏi có sẵn của một khảo sát bất kỳ

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://www.viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",
    'category': 'Marketing/Survey',
    'version': '0.1.0',
    'depends': ['survey'],
    'data': [
        'security/module_security.xml',
        'security/ir.model.access.csv',
        'views/survey_question_bank_views.xml',
        'views/survey_question_bank_category_views.xml',
        'wizard/wizard_survey_import_question_views.xml',
        'wizard/wizard_survey_create_question_bank_views.xml',
        'views/survey_survey_views.xml',
        'views/survey_question_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 190.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
