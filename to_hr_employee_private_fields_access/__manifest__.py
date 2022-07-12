{
    'name': "HR Employee Private Fields Access",
    'name_vi_VN': "Quyền truy cập thông tin riêng tư của nhân viên",

    'summary': """
Employee Private Fields Access""",
    
    'summary_vi_VN': """
Quyền truy cập thông tin riêng tư của nhân viên""", 

    'description': """

What it does
============
Since the access to the address_home_id is restricted to hr.group_hr_user in Odoo 11, this method is implemented to retrieve the address_home_id with sudo() for the users who have no access to this field in some required scenarios.

Key Features
============
Allow users with the User rights of the Employee module to access private information on the employee form via sudo().
    
Supported Editions
==================
1. Community Edition
2. Enterprise Edition
    
    """,
    'description_vi_VN': """
Mô tả
=====
Vì quyền truy cập vào address_home_id bị hạn chế đối với hr.group_hr_user trong Odoo 11, mô đun này được phát triển để hỗ trợ truy xuất address_home_id bằng sudo () cho những người dùng không có quyền truy cập vào trường này trong một số trường hợp bắt buộc.
    
Tính năng nổi bật
=================
Cho phép người dùng với quyền user của mô đun Nhân viên truy xuất thông tin riêng tư trên biểu mẫu nhân viên thông qua câu lệnh sudo ().
    
Ấn bản được hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise
    
    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Hidden',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True, # TODO: remove this in 14 as no one use it
    'application': False,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
