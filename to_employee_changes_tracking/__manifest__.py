{
    'name': "Employee Changes Tracking",
    'name_vi_VN': "Theo Dõi Thay Đổi Thông Tin Nhân Viên",

    'summary': """Track changes made on important fields related to the employee""",
    'summary_vi_VN': """Theo dõi thay đổi trên các trường quan trọng liên quan đến nhân viên""",

    'description': """
**What it does**
================
* An integrated module that allows users to track changes in important HR information fields depending on their authorization to share information.

**Key Features**
================
* In the Employee and Contract tab, you can click on any employee or specific employee contract. All the changes made to those fields above will be logged into the record's Open Chatter area.
* What changes are tracked?

    1. Contract (Employee Contract):

        * Department
        * Contract Type
        * Working Hours (also known as Resource Calendar)
        * Basic Wage
        * Salary Structure

    2. Employee Profile

        * Employee Name
        * Employee Manager
        * Working Address
        * Home / Private Address
        * Job Position
        * Work Phone
        * Mobile Phone
        * Employee Manager
        * Coach
        * Work Location

**Editions Supported**
======================
1. Community Edition
2. Enterprise Edition

    """,
    'description_vi_VN': """
**Mô tả**
=========
* "Theo Dõi Thay Đổi Thông Tin Nhân Viên" là mô đun tích hợp cho phép người dùng theo dõi thay đổi những trường thông tin nhân sự quan trọng tuỳ theo phân quyền chia sẻ thông tin.

**Tính năng nổi bật**
=====================
* Tại mục Nhân viên và Hợp đồng, bạn click chọn vào bất kỳ hồ sơ nhân viên hay hợp đồng nhân viên cụ thể. Mọi thông tin thay đổi sẽ được ghi nhận theo lịch sử tại vùng Chatter.
* Dưới đây là những trường thông tin module này cho phép theo dõi:

    1. Hợp đồng (Hợp đồng Nhân viên):

        * Phòng ban
        * Loại hợp đồng
        * Giờ làm việc (also known as Resource Calendar)
        * Lương cơ bản
        * Cơ cấu lương

    2. Hồ sơ nhân viên

        * Tên nhân viên
        * Tên quản lý
        * Địa chỉ làm việc
        * Nhà / Địa chỉ cá nhân
        * Vị trí
        * Điện thoại làm việc
        * Điện thoại di động
        * Quản lý nhân viên
        * Người huấn luyện
        * Trụ sở làm việc

**Ấn bản hỗ trợ**
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': 'T.V.T Marine Automation (aka TVTMA),Viindoo',
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Human Resources/Employees',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 9.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
