{
    'name': "HR Skill Framework - Recruitment",
    'name_vi_VN': "Khung kỹ năng nhân viên - Tuyển dụng",

    'summary': """
Integrate HR Skill Framework app with Recruitment
""",
    'summary_vi_VN': """
Tích hợp khung kỹ năng nhân viên với tuyển dụng
""",

    'description': """
What it does
============
With this module, HR Officer can see the detail of each skill when reading applicant's profile.
Theses skills description based on Skill Framework, which is builded for each job position requirements.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Với module này, phòng Nhân sự có thể xem được chi tiết các kỹ năng khi đọc hồ sơ ứng viên.
Những mô tả kỹ năng này được dựa trên Khung Kỹ Năng đã được xây dựng để phù hợp với yêu cầu của vị trí công việc.

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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Skills',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_skill_framework','to_hr_skills_recruitment'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_applicant_skill_views.xml',
    ],
    'images' : [
        # 'static/description/main_screenshot.png'
        ],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
