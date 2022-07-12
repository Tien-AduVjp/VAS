import xlsxwriter

from odoo import fields, models, _
from io import BytesIO
from odoo.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def _generate_acb_payroll_payment_xlsx(self):
        self.ensure_one()
        # Create an new Excel file and add a worksheet.
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        # Set dimension for column and Format cells:
        worksheet.set_row(0, 25)
        worksheet.set_row(1, 25)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 40)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 30)
        title_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#969696',
            'font_size': 25,
            'font_name': 'Times New Roman',
            'border': 1,
            })
        cell_format = workbook.add_format({
            'bold': True,
            'bg_color': '#c0c0c0',
            'bottom': 1,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 15
            })
        values_column_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 15
            })
        order_number_column_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'font_name': 'Times New Roman',
            'font_size': 15
            })
        # Header Table:
        title_payroll = 'CHI HO LUONG THANG %s' % self.date_start.strftime('%m-%Y')
        worksheet.merge_range('A1:H1', title_payroll, title_format)
        worksheet.write('A2', 'STT', cell_format)
        worksheet.write('B2', 'Tên NV', cell_format)
        worksheet.write('C2', 'Số tài khoản', cell_format)
        worksheet.write('D2', 'Số tiền', cell_format)
        worksheet.write('E2', 'Nội dung giao dịch', cell_format)
        worksheet.write('F2', 'Số CMND', cell_format)
        worksheet.write('G2', 'Mã NV', cell_format)
        worksheet.write('H2', 'Chức danh', cell_format)

        row = 1
        order_number = 0
        to_base_obj = self.env['to.base']
        # Start preparing data for the xlsx file
        # Slips with zero or negative net amount will not be included in the printed XLSX file.
        for slip in self.slip_ids.filtered(lambda sl: sl.net_salary > 0):
            order_number += 1
            row += 1
            if not slip.employee_id.barcode:
                slip.employee_id.generate_random_barcode()
            # Insert values in columns
            worksheet.write(row, 0, order_number, order_number_column_format)
            worksheet.write(row, 1, to_base_obj.strip_accents(slip.employee_id.name), values_column_format)
            worksheet.write(row, 2, slip.employee_id.bank_account_id.acc_number, values_column_format)
            worksheet.write(row, 3, slip.net_salary, values_column_format)
            worksheet.write(row, 4,
                            "%s - %s" % (to_base_obj.strip_accents(self.company_id.name), to_base_obj.strip_accents(slip.name)),
                            values_column_format
                            )
            worksheet.write(row, 5, int(slip.employee_id.identification_id) or '', values_column_format)
            worksheet.write(row, 6, slip.employee_id.barcode, values_column_format)
            worksheet.write(row, 7, to_base_obj.strip_accents(slip.employee_id.job_id.name or ''), values_column_format)
        workbook.close()
        file_data.seek(0)
        return file_data

    def _get_file_name_acb(self):
        # Create name of attachment file to download
        datetime_now = fields.Datetime.now().strftime('%H:%M:%S _ %d-%m-%Y')
        return 'DS Chi ho luong ACB - %s - Xuat file: %s' % (self.env['to.base'].strip_accents(self.name), datetime_now)

    def download_acb_payslip_batch_payment(self):
        self.ensure_one()
        for slip in self.slip_ids:
            if not slip.employee_id.bank_account_id.acc_number:
                raise ValidationError(_("The employee %s has no bank account specified. Please specify one for the employee first") % slip.employee_id.name)
        return {
            'type': 'ir.actions.act_url',
            'url': '/payroll/payslip_batch_acb_xlsx/%d' % self.id,
            'target': '_blank'
        }
