{
    'name': 'VN-Invoice',
    'name_vi_VN':'Tích hợp VN-Invoice',

    'summary': """
Integrates with VN-Invoice service to issue legal e-Invoice
    """,

    'summary_vi_VN': """
Tích hợp với dịch vụ hoá đơn điện tử VN-Invoice
    """,

    'description':"""
Key Features
============
#. Issue VN-invoices from Odoo Invoices
#. Generate Representation Version (PDF,XML) of the issued invoice and store it in Odoo for later download
#. Generate Converted Version of the issued invoice and store it in Odoo for later download
#. Cancel issued VN-invoices
#. Automatically download Converted and Representation files of issued VN-invoices 
#. Manage Odoo invoices based on VN-invoice status:

   - Not Issued: Odoo invoices that have no corresponding VN-invoice issued
   - Issued and not Paid: Odoo invoices that have corresponding VN-invoice issued but not set as paid
   - Paid: Odoo invoices that have corresponding VN-invoice issued and paid
   - Issued but Cancelled: Odoo invoices that have corresponding VN-invoice issued but cancelled already

#. Easy to define and manage invoice series, invoice templates, invoices type according to the state rules.
#. Invoice Serial can be set for company (in Accounting > Configuration > Settings) and Account Journal so that you will have

   - Multi-company environment support for different invoice serials
   - Multi-Serial support for the same company: you can issue invoices with different serials that you have registered with
     VN-invoice and accepted by the state authority

#. Invoice template can be set for companies (in Accounting > Configuration > Settings) and account journals so that you will have

   - Multi-company environment support for different invoice templates
   - Multi-Template support for the same company: you can issue invoices with different templates that you have registered with
     VN-invoice and accepted by the state authority

#. Invoice type can be set for companies (in Accounting > Configuration > Settings) and account journals so that you will have 

   - Multi-company environment support for different invoice types
   - Multi-Type support for the same company: you can issue invoices with different types that you have registered with
     VN-invoice and accepted by the state authority

#. Send Invoice now attaches VN-invoice instead of the default Odoo invoice template
#. Customer Portal

   - Customer can download the display version of VN-invoice in PDF format that is also embed an EU's Factur-X standard compliance attachment so that she/he can import into her/his own Odoo.
   - Customer can print the display version of the VN-Invoice
   - Customer can download the XML version of VN-Invoice so that she or he can import it any software that support S-Invoice XML
   
#. Support Sandbox mode for your testing before launching in production
#. Smart enough to avoid you from issuing later invoice that have later date than the one of the earlier invoices that have
   not been issued
#. A large of smart and comprehensive messages that can help you on the context so that you can easily solve any issue with
   the integration by on your own before request help from technicians
#. Multilingual support for issuing to foreign customers according to the state rules: Invoice must be presented in Vietnamese
   and may have another language additionally.
   
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Tính năng chính
===============
#. Phát hành Hóa đơn VN từ Hóa đơn Odoo
#. Tạo Phiên bản thể hiên (PDF,XML) của hóa đơn đã phát hành và lưu trữ trong Odoo để tải xuống sau
#. Tạo Phiên bản đã chuyển đổi của hóa đơn đã phát hành và lưu trữ trong Odoo để tải xuống sau
#. Hủy hóa đơn VN-invoices đã phát hành
#. Tự động tải xuống tệp đã chuyển đổi và thể hiện của hóa đơn VN-invoice đã phát hành
#. Quản lý hóa đơn Odoo dựa trên trạng thái hóa đơn VN-invoice:

   - Chưa phát hành: Hóa đơn Odoo không có hóa đơn VN-invoice tương ứng được phát hành
   - Đã phát hành và chưa thanh toán: Hóa đơn Odoo có hóa đơn VN-invoice tương ứng được phát hành nhưng chưa thanh toán
   - Đã thanh toán: Hóa đơn Odoo có hóa đơn VN-invoice tương ứng được phát hành nhưng chưa thanh toán
   - Đã phát hành rồi Hủy: Hóa đơn Odoo có hóa đơn VN-invoice tương ứng đã phát hành rồi hủy

#. Dễ dàng xác định và quản lý ký hiệu hóa đơn, mẫu hóa đơn, loại hóa đơn theo quy định của nhà nước.
#. Ký hiệu hóa đơn có thể được đặt cho công ty (trong Kế toán> Cấu hình> Cài đặt) và Số nhật ký.

   - Hỗ trợ môi trường nhiều công ty cho các ký hiệu hóa đơn khác nhau
   - Hỗ trợ nhiều ký hiệu hóa đơn cho cùng một công ty: bạn có thể xuất hóa đơn với các ký hiệu khác nhau mà bạn đã đăng ký
     hóa đơn VN-invoice và được chấp nhận bởi cơ quan nhà nước

#. Mẫu hóa đơn có thể được đặt cho công ty (trong Kế toán> Cấu hình> Cài đặt) và Số nhật ký

   - Hỗ trợ môi trường nhiều công ty cho các mẫu hóa đơn khác nhau
   - Hỗ trợ nhiều mẫu hóa đơn cho cùng một công ty: bạn có thể xuất hóa đơn với các mẫu khác nhau mà bạn đã đăng ký
     hóa đơn VN-invoice và được chấp nhận bởi cơ quan nhà nước

#. Loại hóa đơn có thể được đặt cho công ty (trong Kế toán> Cấu hình> Cài đặt) và Số nhật ký

   - Hỗ trợ môi trường nhiều công ty cho các loại hóa đơn khác nhau
   - Hỗ trợ nhiều loại hóa đơn cho cùng một công ty: bạn có thể xuất hóa đơn với các loại khác nhau mà bạn đã đăng ký
     hóa đơn VN-invoice và được chấp nhận bởi cơ quan nhà nước

#. Gửi hóa đơn ngay bây giờ đính kèm hóa đơn VN-invoice thay vì mẫu hóa đơn Odoo mặc định
#. Cổng thông tin khách hàng

   - Khách hàng có thể tải xuống phiên bản hiển thị của VN-invoice ở định dạng PDF được đính kèm tệp tuân thủ tiêu chuẩn Factur-X của EU để họ có thể nhập vào Odoo của chính mình.
   - Khách hàng có thể in phiên bản hiển thị của hóa đơn VN-Invoice
   - Khách hàng có thể tải xuống phiên bản XML của VN-Invoice để họ có thể nhập bất kỳ phần mềm nào hỗ trợ VN-Invoice XML
   
#. Hỗ trợ thử nghiệm trước khi vận hành thật
#. Đủ thông minh để tránh bạn phát hành hóa đơn sau đó có ngày muộn hơn một trong những hóa đơn trước đó
#. Một lượng lớn thông điệp thông minh và toàn diện có thể giúp bạn trong bối cảnh để bạn có thể dễ dàng giải quyết mọi vấn đề với
   tự mình tích hợp trước khi có yêu cầu trợ giúp từ kỹ thuật viên
#. Hỗ trợ đa phương để phát hành cho khách hàng nước ngoài theo quy định của nhà nước: Hóa đơn phải được trình bày bằng tiếng Việt
   và có thể có một ngôn ngữ khác bổ sung.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': "https://viindoo.com",
    'live_test_url': "https://v13demo-int.erponline.vn",
    'live_test_url_vi_VN': "https://v13demo-vn.erponline.vn",
    'support': "apps.support@viindoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/tvtma/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'sequence': 31,
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_vn_c200', 'to_einvoice_common', 'to_base'],
    
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/company_data.xml',
        'data/account_vninvoice_type_data.xml',
        'data/account_vninvoice_template_data.xml',
        'data/ir_action_server_data.xml',
        'data/scheduler_data.xml',
        'wizard/account_invoice_einvoice_cancel_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_journal_views.xml',
        'views/account_vninvoice_type_views.xml',
        'views/account_vninvoice_serial_views.xml',
        'views/account_vninvoice_template_views.xml',
        'views/account_move_views.xml',
        'views/account_portal_templates.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 99.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
