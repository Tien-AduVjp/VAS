# -*- coding: utf-8 -*-
{
    'name': "HR Skills Framework",
    'name_vi_VN': "Khung Kỹ năng Nhân sự",

    'summary': """
Build skills and competencies for each and every employee of your company.""",

    'summary_vi_VN': """
Xây dựng khung kỹ năng và năng lực cho mọi nhân viên trong công ty của bạn""",

    'description': """
What it does
============
Build skills and competencies for each and every employee of your company so that each can know exactly what skills she or he are required
to fulfil and what skills are preferred to have.

Required skills for each and every job position and rank in the company will also be visible to employees so that they can know what to do for each node
in their career path.

This application is designed to be compatible with SFIA (The Skills Framework for the Information Age) which is is a model for describing and managing skills
and competencies for professionals working in information and communications technology (ICT), software engineering, and digital transformation.
It is a global common language for describing skills and competencies in the digital world.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================
Xây dựng khung kỹ năng và năng lực cho mọi nhân viên trong công ty của bạn để họ có thể biết chính xác các kỹ năng bắt buộc họ phải đạt được
cũng như các kỹ năng có thì tốt.

Các kỹ năng bắt buộc đối với từng chức vụ và chức danh trong công ty cũng được minh bạch hóa đến mọi nhân viên để họ có thể biết chính xác
họ cần phải đáp ứng những kỹ năng gì cho từng nút trong lộ trình thăng tiến của họ.

Ứng dụng này được thiết kế tương thích với SFIA (The Skills Framework for the Information Age - Khung Kỹ năng cho Thời đại Thông tin), một mô hình
để mô tả và xây dựng khung kỹ năng và năng lực để làm việc chuyên nghiệp trong kỷ nguyên công nghệ thông tin (ICT), công nghiệp phần mềm và chuyển
đổi số. Nói cách khác, SFIA là một ngôn ngữ chung để mô tả khung kỹ năng và năng lực cho thế giới số.

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
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Skills',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['viin_hr_rank', 'hr_skills'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'data/data.xml',
        'views/root_menu.xml',
        'views/hr_employee_grade_views.xml',
        'views/hr_skill_views.xml',
        'views/hr_role_views.xml',
        'views/hr_rank_views.xml',
        'views/hr_department_views.xml',
        'views/hr_skill_description_abstract_views.xml',
        'views/hr_skill_description_views.xml',
        'views/hr_rank_skill_description_views.xml',
        'views/hr_skill_type_views.xml',
        'views/hr_job_view.xml',
        'report/hr_employee_skill_report_views.xml',
        'views/hr_employee_public_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_employees_skill_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'data/demo.xml',
    ],
    'images': [
    	 'static/description/main_screenshot.png'
    	],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 199.9,
    'subscription_price': 6.62,
    'currency': 'EUR',
    'license': 'OPL-1',
}
