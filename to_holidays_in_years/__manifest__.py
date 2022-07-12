{
    'name': "Holidays in Lunar Year",
    'name_vi_VN': "Ngày lễ trong năm theo Âm Lịch",
    'summary': """Holidays in Lunar Calendar""",
    'summary_vi_VN': """Ngày lễ trong năm theo Âm Lịch""",
    'description': """
What it does
============
* In some Asian countries, in addition to normal holidays according to the Solar Calendar, workers are also allocated additional days off according to the lunar calendar (like the Lunar New Year holiday in China, in Vietnam).
* This module (to_holidays_in_years) is developed on top of the python-lunardate library to provide conversion from Lunar Calendar into Odoo's resource calendar.
* You can find the "Holidays in Years" menu in "Settings" when installed.

Key Features
============
* Create Holidays according to the date type (LUNAR/ SOLAR CALENDAR) and Holiday type (National Holiday / Other Holiday).
* Keep track of public holidays of the year.

Credit
------
* Thanks to the development of the python-lunardate by lidaobing https://github.com/lidaobing/python-lunardate
    
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
Mô tả
=====
* Tại một số quốc gia Châu Á, ngoài ngày nghỉ Lễ theo lịch Dương, người lao động còn được phân bổ thêm số ngày nghỉ theo lịch Âm, ví dụ như nghỉ Tết Nguyên đán ở Trung Quốc, ở Việt Nam, v.v. Tuy nhiên, Odoo không hỗ trợ tính năng này. 
* Mô đun "Ngày Lễ trong năm theo Âm lịch" (to_holidays_in_years) được phát triển dựa theo thư viện python-lunardate để cung cấp công cụ chuyển đổi từ lịch Âm sang lịch Dương (lịch của Odoo).
* Bạn có thể tìm thấy menu "Ngày lễ trong năm" trong phần "Thiết lập" sau khi hoàn tất cài đặt.

Tính năng nổi bật
=================
* Tạo ngày Lễ theo kiểu ngày (Lịch Âm/Lịch Dương) và kiểu ngày Lễ (Ngày Lễ quốc gia/Ngày Lễ khác).
* Theo dõi các ngày nghỉ Lễ trong năm.

Lời cảm ơn
----------
Chân thành cảm ơn sự phát triển thư viện python-lunardate của lidaobing https://github.com/lidaobing/python-lunardate

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['resource'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/holiday_year_views.xml'
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
