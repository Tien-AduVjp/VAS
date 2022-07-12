{
    'name': "Survey Results Recomputation",
    'name_vi_VN': "Tính lại kết quả khảo sát",

    'summary': """
Recompute answer score of results of survey.
        """,

    'summary_vi_VN': """
Tính lại điểm của kết quả khảo sát.
    	""",

    'description': """
Sometimes answers score were wrong and we need recompute results from survey. This module provide a button on survey form
to allow recompute results after correct answers

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Đôi khi việc tính điểm của các câu trả lời bị sai với lý do các thiết lập trước đó trên survey bị sai. Khi đó,
chúng ta cần điều chỉnh lại các câu trả lời trên form Khảo sát và tính toán lại điểm của các kết quả đã hoàn thành trước đó.
Mô đun này cung câp thêm một nút trên form Khảo sát để tính toán lại điểm của các kết quả đã có sau khi điều chỉnh lại Khảo sát.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': "support@viindoo.com",
    'category': 'Marketing/Survey',
    'version': '0.1',
    'depends': ['survey'],
    'data': [
        'views/survey_survey_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
