import xlsxwriter
from io import BytesIO
from odoo import fields, models, _
from odoo.tools.misc import get_lang, DEFAULT_SERVER_DATE_FORMAT, format_date


class WizardL10n_vn_s07dn(models.TransientModel):
    _name = 'l10n_vn.s07dn'
    _inherit = 'account.common.report'
    _description = 'VietNam S07dn Report Wizard'

    def _default_account_ids(self):
        account_ids = self.env['account.account'].search([('code', '=like', '111%')])
        return account_ids

    date_from = fields.Date(default=fields.Date.today().replace(day=1, month=1), required=True, string='Date from')
    date_to = fields.Date(default=fields.Date.today, required=True, string='Date to')
    account_ids = fields.Many2many('account.account', string='Accounts', default=_default_account_ids, domain="[('code', '=like', '111%')]", required=True)

    def _prepare_check_report(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id', 'account_ids'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=get_lang(self.env).code)
        return data

    def check_report(self):
        self.ensure_one()
        data = self._prepare_check_report()
        return self.with_context(discard_logo_check=True)._print_report(data)

    def _build_contexts(self, data):
        result = super(WizardL10n_vn_s07dn, self)._build_contexts(data)
        result['account_ids'] = data['form'].get('account_ids', False)
        return result

    def _print_report(self, data):
        res = self.env.ref('to_account_reports_l10n_vn.report_l10n_vn_s07dn_action').report_action(self, data=data)
        return res

    def check_report_excel(self):
        self._validate_date_from_and_date_to(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_url',
            'url': '/account-cash-book/download/xlsx/%d' % self.id,
            'target': '_blank'
        }

    def report_excel(self):
        self.ensure_one()
        data = self._prepare_check_report()
        return self._export_excel(data)

    def _data_report_excel(self, data):
        data['form']['date_from'] = data['form']['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['used_context']['date_from'] = data['form']['used_context']['date_from'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['date_to'] = data['form']['date_to'].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data['form']['used_context']['date_to'] = data['form']['used_context']['date_to'].strftime(DEFAULT_SERVER_DATE_FORMAT)

        lines = self.env['report.to_account_reports_l10n_vn.report_s07dn']._get_lines(data)

        dict_data = {
            'data': data,
            'lines': lines,
            'account_ids': False
            }
        dict_data['account_ids'] = 'account_ids' in data['form'] and (', '.join(self.env['account.account'].browse(data['form']['account_ids']).mapped('code')))
        dict_data['today'] = fields.Date.today()
        return dict_data

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
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 25)
        worksheet.set_column(3, 3, 25)
        worksheet.set_column(4, 4, 35)
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
                                            'bold': True,
                                            'font_size': 12,
                                            'font_name': 'Times New Roman'
                                        })
        # Add data default into file excel
        date_from = format_date(self.env, data['data']['form']['date_from'])
        date_to = format_date(self.env, data['data']['form']['date_to'])

        title_rule = _('Template: S07DN \n (Released Under the Circular No. 200/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('H1:J3', title_rule, title_template)
        worksheet.merge_range('E3:G3', _('CASH BOOK'), title_report_format)
        worksheet.merge_range('E4:G4', _('Accounts: ') + str(data["account_ids"]), content_cell_format)
        worksheet.merge_range('E5:G5', _('Date From: ') + date_from + _('- Date To: ') + date_to, date_format)
        worksheet.write('I7', _('Currency:'), currency_format)
        worksheet.write('J7', self.company_id.currency_id.name, currency_format)
        # Header Table
        worksheet.merge_range('A8:A9', _('Posting \n Date'), name_style_format)
        worksheet.merge_range('B8:B9', _('Voucher \n Date'), name_style_format)
        worksheet.merge_range('C8:D8', _('Voucher No.'), name_style_format)
        worksheet.merge_range('E8:E9', _('Description'), name_style_format)
        worksheet.merge_range('F8:F9', _('Counterpart \n Accounts'), name_style_format)
        worksheet.merge_range('G8:I8', _('Amount'), name_style_format)
        worksheet.merge_range('J8:J9', _('Note'), name_style_format)
        
        worksheet.write('C9', _('Receipt'), name_style_format)
        worksheet.write('D9', _('Payment'), name_style_format)
        worksheet.write('G9', _('Receipt'), name_style_format)
        worksheet.write('H9', _('Payment'), name_style_format)
        worksheet.write('I9', _('Balance'), name_style_format)
        
        worksheet.write('A10', _('A'), name_style_format)
        worksheet.write('B10', _('B'), name_style_format)
        worksheet.write('C10', _('C'), name_style_format)
        worksheet.write('D10', _('D'), name_style_format)
        worksheet.write('E10', _('E'), name_style_format)
        worksheet.write('F10', _('F'), name_style_format)
        worksheet.write('G10', _('1'), name_style_format)
        worksheet.write('H10', _('2'), name_style_format)
        worksheet.write('I10', _('3'), name_style_format)
        worksheet.write('J10', _('G'), name_style_format)

        # Insert values into cell content body table
        row = 11
        for line in data['lines']:
            worksheet.set_row(row, 20)
            if line['type'] == 'account_title':
                worksheet.merge_range('A{0}:J{0}'.format(row), line.get('account_name', ''), account_title_format)
            else:
                name = line['name'] and line['name'].replace('<br/>', '\n') or ''
                worksheet.write('E%s' % row, name, interval_format)
                worksheet.write('J%s' % row, ' ', interval_format)
                if line['type'] == 'move_line':
                    worksheet.write('A%s' % row, format_date(self.env, line['date']), date_format_table)
                    worksheet.write('B%s' % row, format_date(self.env, line['ref_date']), date_format_table)
                    if line['debit'] != 0:
                        worksheet.write('C%s' % row, line['ref_name'], interval_format)
                    else:
                        worksheet.write('C%s' % row, ' ', interval_format)
                    if line['credit'] != 0:
                        worksheet.write('D%s' % row, line['ref_name'], interval_format)
                    else:
                        worksheet.write('D%s' % row, ' ', interval_format)
                    worksheet.write('F%s' % row, line['account_id'], interval_format_values)
                    worksheet.write('G%s' % row, line['debit'], interval_format_values)
                    worksheet.write('H%s' % row, line['credit'], interval_format_values)
                else:
                    worksheet.merge_range('A{0}:D{0}'.format(row), '', interval_format_values)
                    if line['type'] == 'account_total':
                        worksheet.write('G%s' % row, line['debit'], interval_format_values)
                        worksheet.write('H%s' % row, line['credit'], interval_format_values)
                    else:
                        worksheet.merge_range('G{0}:H{0}'.format(row), '', interval_format_values)
                worksheet.write('I%s' % row, line['progress'], interval_format_values)

            row += 1

        # Footer

        worksheet.merge_range('A{0}:C{0}'.format (row + 2), _('- Issue Date: ') + format_date(self.env, data['today']), content_cell_format_title)                                          

        worksheet.merge_range('A{0}:B{0}'.format(row + 4), _('Prepared By'), name_style_format_title)
        worksheet.merge_range('A{0}:B{0}'.format(row + 5), _('(Signature, Full Name)'), content_cell_format)

        worksheet.merge_range('E{0}:F{0}'.format(row + 4), _('Chief Accountant'), name_style_format_title)
        worksheet.merge_range('E{0}:F{0}'.format(row + 5), _('(Signature, Full Name)'), content_cell_format)

        worksheet.merge_range('H{0}:J{0}'.format (row + 3), _('Month ..... Day ..... Year .....'), content_cell_format)
        worksheet.merge_range('H{0}:J{0}'.format(row + 4), _('Director/CEO'), name_style_format_title)
        worksheet.merge_range('H{0}:J{0}'.format(row + 5), _('(Signature, Full Name, Job Title)'), content_cell_format)

        workbook.close()
        # Back cusor the beginning of the file
        file_data.seek(0)
        return file_data
