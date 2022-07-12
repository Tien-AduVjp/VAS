{
    'name': "HR Expense & Payroll Integration",
    'name_vi_VN': 'Tích hợp Chi tiêu nhân sự và Bảng lương',

    'summary': """
Reimburse HR Expenses in Payroll with Payslips""",

    'summary_vi_VN': """
Hoàn trả Chi tiêu Nhân sự trong Bảng lương với Phiếu lương""",

    'description': """
What it does
============

This application provide integration between the HR Expense application and HR Payroll application to move HR expense reimburse to payslip.
In other words, instead of paying back to the employee immediately after the expense is approved, the expense amount will be postponed for including in the next payslip.

Key Features
============

#. HR Expense

   * During HR Expense submission, employee can suggest reimbursement in payslip thanks to the new option "Reimbursed in Payslip" added to the HR Expense form.
   * During approval, manager can decide either the reimbursement will be made immediately on the corresponding HR Expense or postpone it for the next payslip.
   * No accounting entry will be created at any stage of HR Expense if the expense is set to be reimbursed in Payslip.

#. Payslip

   * When the "Compute Sheet" button, Odoo will search for all the approved HR expenses of the corresponding employee that are marked with "Reimbursed in Payslip" and add them to the payslip so that salary rules can access it with the dot syntax **payslip.hr_expense_ids**.
   * When the "Confirm" button is hit, Odoo will "Compute Sheet" before doing confirmation.
   * When the payslip is set as Done, all the related HR Expenses will be set as Done at the same time.

#. Salary Rules Access

   * **result = sum(payslip.hr_expense_ids.mapped(total_amount))** will summarize all the expenses amount and return the result for the salary rule.
   * **result = sum(payslip.hr_expense_ids.filtered(lambda exp: 'Air Ticket' in exp.product_id.name).mapped(total_amount))** will summarize all the expenses amount concerning 'Air Ticket' and return the result for the salary rule.
   * etc.

Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Ứng dụng này làm gì
===================

Ứng dụng này cung cấp tích hợp giữa ứng dụng Chi tiêu nhân sự và ứng dụng Bảng lương Nhân sự để chuyển hoàn trả Chi tiêu nhân sự sang phiếu lương.
Nói cách khác, thay vì trả lại cho nhân viên ngay sau chi tiêu được phê duyệt, số tiền chi tiêu sẽ được giữ lại để bao gồm trong phiếu lương tiếp theo.

Các tính năng chính
===================

#. Chi tiêu Nhân sự

   * Trong quá trình nộp Chi tiêu Nhân sự, nhân viên có thể đề xuất hoàn trả trong phiếu lương nhờ vào tùy chọn mới "Hoàn trả trong phiếu lương" được thêm vào biểu mẫu Chi tiêu Nhân sự
   * Trong quá trình phê duyệt, người quản lý có thể quyết định việc hoàn trả sẽ được thực hiện ngay lập tức trên biểu mẫu Chi tiêu Nhân sự tương ứng hoặc hoãn lại cho phiếu lương tiếp theo
   * Không có bút toán kế toán nào được tạo ra ở bất kì giai đoạn nào của Chi tiêu Nhân sự nếu chi tiêu được đặt là được hoàn trả trong Phiếu lương

#. Phiếu Lương

   * Khi nút nhấn nút "Tính toán Phiếu lương", Odoo sẽ tìm kiếm tất cả các chi tiêu nhân sự được phê duyệt của nhân viên tương ứng được đánh dấu bằng "Hoàn trả trong phiếu lương" và thêm chúng vào phiếu lương để quy tắc lương có thể truy cập bằng cú pháp dấu chấm ** paylip.hr_exense_ids **
   * Khi nhấn nút "Xác nhận", Odoo sẽ chạy "Tính toán Phiếu lương" trước khi thực hiện xác nhận
   * Khi phiếu thanh toán chuyển trạng thái Hoàn thành, tất cả các Chi tiêu Nhân sự liên quan sẽ được chuyển trạng thái Hoàn thành cùng một lúc.

#. Truy cập quy tắc lương

   * **result = sum(payslip.hr_expense_ids.mapped(total_amount))** sẽ tổng hợp tất cả các khoản chi tiêu và trả lại kết quả cho quy tắc lương
   * **result = sum(payslip.hr_expense_ids.filtered(lambda exp: 'Air Ticket' in exp.product_id.name).mapped(total_amount))** sẽ tóm tắt tất cả số tiền chi tiêu liên quan đến 'Vé máy bay' và trả lại kết quả cho quy tắc lương
   * v.v.

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': "https://v14demo-int.viindoo.com",
    'live_test_url_vi_VN': "https://v14demo-vn.viindoo.com",
    'support': 'apps.support@viindoo.com',
    'category': 'Human Resources',
    'version': '0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense', 'to_hr_expense', 'to_hr_payroll', 'to_hr_payroll_account'],

    # always loaded
    'data': [
        'security/hr_expense_security.xml',
        'security/ir.model.access.csv',
        'data/hr_contribution_category_data.xml',
        'views/hr_expense_sheet_views.xml',
        'views/hr_expense_views.xml',
        'views/hr_payslip_views.xml',
    ],
    'images' : ['static/description/main_screenshot.png'],
    'installable': True,
    'application': False,
    'auto_install': ['hr_expense', 'to_hr_payroll'],
    'post_init_hook': 'post_init_hook',
    'price': 45.9,
    'currency': 'EUR',
    'license': 'OPL-1',
}
