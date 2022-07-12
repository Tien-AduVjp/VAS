from odoo import http
from odoo.http import request, content_disposition


class PayslipPortal(http.Controller):

    @http.route('/payroll/payslip_batch_acb_xlsx/<int:hr_payslip_run_id>', type='http', auth='user')
    def download_payslip_batch_acb_xlsx(self, hr_payslip_run_id, **kwargs):
        hr_payslip_run = request.env['hr.payslip.run'].browse(hr_payslip_run_id)
        file_data = hr_payslip_run._generate_acb_payroll_payment_xlsx()
        file_name = '%s.xlsx' % hr_payslip_run._get_file_name_acb()
        content_length = len(file_data.getvalue())
        http_headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),  # xlsx mimetype
            ('Content-Length', content_length),
            ('Content-Disposition', content_disposition(file_name))
             ]
        return request.make_response(file_data, headers=http_headers)

