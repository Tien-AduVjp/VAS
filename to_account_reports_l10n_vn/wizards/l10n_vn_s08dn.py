import xlsxwriter
from io import BytesIO
from odoo import fields, models, _
from odoo.tools.misc import format_date


class WizardL10n_vn_s08dn(models.TransientModel):
    _name = 'l10n_vn.s08dn'
    _inherit = 'l10n_vn.s07dn'
    _description = 'VietNam S08dn Report Wizard'

    def _default_account_ids(self):
        account_ids = self.env['account.account'].search([('code', '=like', '112%')])
        return account_ids

    account_ids = fields.Many2many('account.account', string='Accounts', default=_default_account_ids, domain="[('code', '=like', '112%')]", required=True)

    def _print_report(self, data):
        res = self.env.ref('to_account_reports_l10n_vn.report_l10n_vn_s08dn_action').report_action(self, data=data)
        return res

    def check_report_excel(self):
        self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/account-bank-book/download/xlsx/%d' % self.id,
            'target': '_blank'
        }

    def _export_excel(self, data):
        '''Method Create file Excel'''
        self.ensure_one()

        # get data
        data = self._data_report_excel(data)

        # Create an new Excel file and add a worksheet.
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 35)
        worksheet.set_column(4, 4, 30)
        worksheet.set_column(5, 5, 20)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        worksheet.set_row(0, 20)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 30)
        worksheet.set_row(7, 25)
        worksheet.set_row(8, 30)
        worksheet.set_row(9, 25)

        # Add a bold format to use to highlight cells.
        title_report_format = workbook.add_format({'bold': True,
                                    'font_name': 'Times New Roman',
                                    'align':'center',
                                    'valign': 'vcenter',
                                    'font_size': 16,
                                    'font_name': 'Times New Roman'})
        title_template = workbook.add_format({'font_size': 12,
                                              'valign': 'vcenter',
                                              'align':'center',
                                              'text_wrap': True,
                                              'font_name': 'Times New Roman'})
        title_company_info = workbook.add_format({'font_size': 12,
                                              'valign': 'vcenter',
                                              'align':'left',
                                              'text_wrap': True,
                                              'font_name': 'Times New Roman'})
        interval_format = workbook.add_format({'border': 1,
                                               'font_size': 12,
                                               'text_wrap': True,
                                               'font_name': 'Times New Roman'})
        interval_format_values = workbook.add_format({'border': 1,
                                               'font_size': 12,
                                               'text_wrap': True,
                                               'num_format': '#,##0',
                                               'font_name': 'Times New Roman'})
        date_format = workbook.add_format({'align': 'center',
                                            'font_size': 12,
                                            'text_wrap': True,
                                            'font_name': 'Times New Roman'})
        date_format_table = workbook.add_format({'border': 1,
                                            'align': 'center',
                                            'font_size': 12,
                                            'text_wrap': True,
                                            'font_name': 'Times New Roman'})
        currency_format = workbook.add_format({'align': 'left',
                                            'font_size': 12,
                                            'text_wrap': True,
                                            'font_name': 'Times New Roman'})
        name_style_format = workbook.add_format({'bold': True,
                                           'bg_color': '#87CEFA',
                                           'bottom': 1,
                                           'align':'center',
                                           'valign': 'vcenter',
                                           'text_wrap': True,
                                           'border': 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 12})
        content_cell_format = workbook.add_format({
                                            'align':'center',
                                            'font_name': 'Times New Roman'
                                        })
        name_style_format_title = workbook.add_format({'bold': True,
                                            'align':'center',
                                            'font_name': 'Times New Roman'
                                        })
        content_cell_format_title = workbook.add_format({
                                            'font_size': 12,
                                            'font_name': 'Times New Roman'
                                        })
        account_title_format = workbook.add_format({
                                            'font_size': 12,
                                            'bold': True,
                                            'font_name': 'Times New Roman'
                                        })

        # Add data default into file excel
        date_from = format_date(self.env, data['data']['form']['date_from'])
        date_to = format_date(self.env, data['data']['form']['date_to'])

        title_rule = _('Template: S08DN \n (Released Under the Circular No. 200/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('G1:I3', title_rule, title_template)
        worksheet.merge_range('D3:F3', _('CASH IN BANK DEPOSIT BOOK'), title_report_format)
        worksheet.merge_range('D4:F4', _('Accounts: ') + str(data['account_ids']), content_cell_format)
        worksheet.merge_range('D5:F5', _('Date From: ') + date_from + _('- Date To: ') + date_to, date_format)
        worksheet.merge_range('D6:F6', _('Address To Open Trading Account: ... ...'), date_format)
        worksheet.merge_range('D7:F7', _('Account Number At The Place Of Sending: ... ...'), date_format)
        worksheet.write('H9', _('Currency:'), currency_format)
        worksheet.write('I10', self.company_id.currency_id.name, currency_format)
        # Header Table
        worksheet.merge_range('A10:A11', _('Posting \n Date'), name_style_format)
        worksheet.merge_range('B10:C10', _('Voucher'), name_style_format)
        worksheet.merge_range('D10:D11', _('Description'), name_style_format)
        worksheet.merge_range('E10:E11', _('Counterpart \n Accounts'), name_style_format)
        worksheet.merge_range('F10:H10', _('Amount'), name_style_format)
        worksheet.merge_range('I10:I11', _('Note'), name_style_format)

        worksheet.write('B11', _('No.'), name_style_format)
        worksheet.write('C11', _('Date'), name_style_format)
        worksheet.write('F11', _('Receipt \n (Deposit)'), name_style_format)
        worksheet.write('G11', _('Payment \n (WithDraw)'), name_style_format)
        worksheet.write('H11', _('Balance'), name_style_format)

        worksheet.write('A12', _('A'), name_style_format)
        worksheet.write('B12', _('B'), name_style_format)
        worksheet.write('C12', _('C'), name_style_format)
        worksheet.write('D12', _('D'), name_style_format)
        worksheet.write('E12', _('E'), name_style_format)
        worksheet.write('F12', _('1'), name_style_format)
        worksheet.write('G12', _('2'), name_style_format)
        worksheet.write('H12', _('3'), name_style_format)
        worksheet.write('I12', _('F'), name_style_format)

        # Insert values into cell content body table
        row = 13
        for line in data['lines']:
            worksheet.set_row(row, 20)
            if line['type'] == 'account_title':
                worksheet.merge_range('A{0}:I{0}'.format(row), line.get('account_name', ''), account_title_format)
            else:
                name = line['name'] and line['name'].replace('<br/>', '\n') or ''
                worksheet.write('D%s' % row, name, interval_format)
                worksheet.write('I%s' % row, ' ', interval_format)
                if line['type'] == 'move_line':
                    worksheet.write('A%s' % row, format_date(self.env, line['date']), date_format_table)
                    worksheet.write('B%s' % row, line['ref_name'], interval_format)
                    worksheet.write('C%s' % row, format_date(self.env, line['ref_date']), date_format_table)
                    worksheet.write('E%s' % row, line['account_id'], interval_format)
                    worksheet.write('F%s' % row, line['debit'], interval_format)
                    worksheet.write('G%s' % row, line['credit'], interval_format)
                else:
                    worksheet.merge_range('A{0}:C{0}'.format(row), '', interval_format_values)
                    worksheet.write('E%s' % row, ' ', interval_format_values)
                    if line['type'] == 'account_total':
                        worksheet.write('F%s' % row, line['debit'], interval_format_values)
                        worksheet.write('G%s' % row, line['credit'], interval_format_values)
                    else:
                        worksheet.merge_range('F{0}:G{0}'.format(row), '', interval_format_values)
                worksheet.write('H%s' % row, line['progress'], interval_format_values)

            row += 1

        # Footer

        worksheet.merge_range('A{0}:C{0}'.format (row + 2), _('- Issue Date: ') + format_date(self.env, data['today']), content_cell_format_title)

        worksheet.merge_range('A{0}:B{0}'.format(row + 4), _('Prepared By'), name_style_format_title)
        worksheet.merge_range('A{0}:B{0}'.format(row + 5), _('(Signature, Full Name)'), content_cell_format)

        worksheet.merge_range('D{0}:E{0}'.format(row + 4), _('Chief Accountant'), name_style_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(row + 5), _('(Signature, Full Name)'), content_cell_format)

        worksheet.merge_range('G{0}:I{0}'.format (row + 3), _('Month ..... Day ..... Year .....'), content_cell_format)
        worksheet.merge_range('G{0}:I{0}'.format(row + 4), _('Director/CEO'), name_style_format_title)
        worksheet.merge_range('G{0}:I{0}'.format(row + 5), _('(Signature, Full Name, Job Title)'), content_cell_format)

        workbook.close()
        # Back cusor the beginning of the file
        file_data.seek(0)

        return file_data
