{
    'name': "Payroll By Administrative Regions - Vietnam",
    'name_vi_VN': "Bảng lương Theo Vùng Hành Chính - Việt Nam",

    'summary': """Localize the Payroll By Administrative Regions for Vietnam""",
    'summary_vi_VN': """Bản địa hóa Bảng lương Theo Vùng Hành Chính cho Việt Nam""",

    'description': """
What it does
============
* This module add Vietnam localized data for its administrative regions

   * Maximum Labor Union Contribution per month by employees
   * Minimum wage for each administrative region in Vietnam
   * Minimum/Maximum Contribution Base for each contribution type according to Administrative Regions in Vietnam

Supported Editions
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Mô tả
=====
* Module này cập nhật một số dữ liệu theo Vùng hành chính của Việt Nam:

   * Mức đóng góp công đoàn tối đa mỗi tháng của nhân viên
   * Mức lương tối thiểu cho từng vùng hành chính tại Việt Nam
   * Cơ sở đóng góp tối thiểu / tối đa cho từng kiểu đóng góp theo vùng hành chính tại Việt Nam

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
    'category': 'Human Resources/Payroll',
    'version': '0.1.0',
    'depends': ['to_l10n_vn_hr_payroll','viin_hr_payroll_administrative_region'],

    # always loaded
    'data': [
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
