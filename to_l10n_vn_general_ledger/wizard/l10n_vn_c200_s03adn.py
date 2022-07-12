import xlsxwriter

from io import BytesIO

from odoo import models, fields, _
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, format_date, formatLang

    
class WizardL10n_vnC200_s03adn(models.TransientModel):
    _name = 'wizard.l10n_vn.c200_s03adn'    
    _inherit = "account.common.report"
    _description = 'Vietnam C200 S03a-DN Report Wizard'        
    
    date_from = fields.Date(default=fields.Date.today().replace(day=1, month=1))    
    date_to = fields.Date(default=fields.Date.today)
       
    target_move = fields.Selection([
        ('posted', 'All Posted Entries'),
        ('all', 'All Entries'),
        ], string='Target Moves')

    def _print_report(self, data):
        res = self.env.ref('to_l10n_vn_general_ledger.act_report_c200_s03adn').report_action(self, data=data)
        return res
    
    def generate_file_xlsx(self):
        self.ensure_one()
        data = self._prepare_data()
        return self._export_excel(data)
    
    def check_report_excel(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/general_ledger/c200_s03adn_export_xlsx/%d' % self.id,
            'target': '_blank'
        }
    
    def _prepare_data(self):
        self.ensure_one()
        data = {}
        # Get data context
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        
        # Format date
        data["form"]["date_from"] = data["form"]["date_from"].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data["form"]["used_context"]["date_from"] = data["form"]["used_context"]["date_from"].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data["form"]["date_to"] = data["form"]["date_to"].strftime(DEFAULT_SERVER_DATE_FORMAT)
        data["form"]["used_context"]["date_to"] = data["form"]["used_context"]["date_to"].strftime(DEFAULT_SERVER_DATE_FORMAT)
        
        # Get line
        lines = self.env['report.to_l10n_vn_general_ledger.report_c200_s03adn']._get_lines(data)
        dict_data = {
            "data": data,
            "lines": lines,
            "account_ids": False,
            "journal_ids": False,
            "partner_ids": False
            }
        
        return dict_data
    
    def _build_contexts(self, data):
        self.ensure_one()
        result = super(WizardL10n_vnC200_s03adn, self)._build_contexts(data)
        result['target_type'] = data['form'].get('target_type', False)
        if result['target_type'] == 'account':
            result['account_ids'] = data['form'].get('account_ids', False)
            result['journal_ids'] = False
        else:
            result['account_ids'] = False
        return result
    
    def _export_excel(self, data):
        """ Method use create file Excel"""
        self.ensure_one()
        
        # Create an new Excel file and add a worksheet.
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        worksheet = workbook.add_worksheet()
        
        # Set dimension for column and Format cells:
        worksheet.fit_to_pages(1, 0)
        worksheet.set_zoom(80)
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 20)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 40)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 12)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 12)
        worksheet.set_column(11, 11, 12)
        worksheet.set_column(12, 12, 20)
        worksheet.set_row(0, 20)
        worksheet.set_row(1, 20)
        worksheet.set_row(2, 20)
        worksheet.set_row(4, 20)
        worksheet.set_row(5, 20)
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
        date_format = workbook.add_format({'align': 'center',
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
        table_content_style_left_wrap = workbook.add_format({
                                           'align':'left',
                                           'text_wrap': True,
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 12})
        table_content_style_right = workbook.add_format({
                                           'align':'right',
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                           'num_format': "#,##0"})
        table_content_style_center = workbook.add_format({
                                           'align':'center',
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11})
        table_content_style_right_two_decimal = workbook.add_format({
                                           'align':'right',
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 12,
                                           'num_format': "#,##0.00"})
        footer_content_center = workbook.add_format({
                                           'align':'center',
                                           'font_name': 'Times New Roman',
                                           'font_size': 12})
        footer_content_center_bold = workbook.add_format({
                                           'align':'center',
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                           'bold': True})
        
        #         Add data default into file excel
        date_from = format_date(self.env, data["data"]["form"]["date_from"])
        date_to = format_date(self.env, data["data"]["form"]["date_to"])
        
        worksheet.merge_range('E3:J4', _('GENERAL LEDGER'), title_report_format)
        worksheet.merge_range('E5:J5', _('Date From: ') + date_from + _(' - Date To: ') + date_to, date_format)
        worksheet.merge_range('F7:G7', _('Currency:'), currency_format)
        worksheet.write('H7', self.company_id.currency_id.name, currency_format)
        
        #         Header Table
        worksheet.merge_range('A8:A9', _('No.'), name_style_format)
        worksheet.merge_range('B8:B9', _('Date'), name_style_format)
        worksheet.merge_range('C8:D8', _('Origin'), name_style_format)
        worksheet.merge_range('E8:E9', _('Description'), name_style_format)
        worksheet.merge_range('F8:F9', _('Registered'), name_style_format)
        worksheet.merge_range('G8:G9', _('Account'), name_style_format)
        worksheet.merge_range('H8:H9', _('Counterpart \nAccounts'), name_style_format)
        worksheet.merge_range('I8:I9', _('Debit'), name_style_format)
        worksheet.merge_range('J8:J9', _('Credit'), name_style_format)
        worksheet.merge_range('K8:K9', _('Amount \n Currency'), name_style_format)
        worksheet.merge_range('L8:L9', _('Exchange \n Rate'), name_style_format)
        worksheet.merge_range('M8:M9', _('Partner'), name_style_format)
        
        worksheet.write('C9', _('Origin No.'), name_style_format)
        worksheet.write('D9', _('Origin Date'), name_style_format)
        
        worksheet.write('A10', _('1'), name_style_format)
        worksheet.write('B10', _('2'), name_style_format)
        worksheet.write('C10', _('3'), name_style_format)
        worksheet.write('D10', _('4'), name_style_format)
        worksheet.write('E10', _('5'), name_style_format)
        worksheet.write('F10', _('6'), name_style_format)
        worksheet.write('G10', _('7'), name_style_format)
        worksheet.write('H10', _('8'), name_style_format)
        worksheet.write('I10', _('9'), name_style_format)
        worksheet.write('J10', _('10'), name_style_format)
        worksheet.write('K10', _('11'), name_style_format)
        worksheet.write('L10', _('12'), name_style_format)
        worksheet.write('M10', _('13'), name_style_format)

        # create lines
        row = 11
        line_no = 0
        for line in data["lines"]:
            worksheet.set_row(row - 1, 25)
            table_content_style_right_currency = workbook.add_format({
                                           'align':'right',
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                           'num_format': "#,##0"
                                           })
            table_content_style_right_amount_currency = workbook.add_format({
                                           'align':'right',
                                           'border' : 1,
                                           'font_name': 'Times New Roman',
                                           'font_size': 11,
                                            'num_format': "#,##0.00 [$%s];-#,##0.00 [$%s]" % (line.get('symbol_amount_currency'), line.get('symbol_amount_currency'))
                                           })
            line_no = line_no + 1
            worksheet.write('A%s' % row, line_no, table_content_style_right)
            if line['state'] == 'posted':
                worksheet.write('B%s' % row, format_date(self.env, line['date']), table_content_style_left_wrap)
                worksheet.write('F%s' % row, 'X', table_content_style_center)
            else:
                worksheet.write('B%s' % row, '', table_content_style_left_wrap)
                worksheet.write('F%s' % row, '', table_content_style_center)
                
            worksheet.write('C%s' % row, line['move_name'], table_content_style_left_wrap)
            worksheet.write('D%s' % row, format_date(self.env, line['move_date']), table_content_style_left_wrap)
            worksheet.write('E%s' % row, line['lname'], table_content_style_left_wrap)
            worksheet.write('G%s' % row, line['account_code'], table_content_style_right)
            worksheet.write('H%s' % row, line['counterpart'], table_content_style_right)
            worksheet.write('I%s' % row, line['debit'], table_content_style_right_currency)
            worksheet.write('J%s' % row, line['credit'], table_content_style_right_currency)
            if line['amount_currency']:
                worksheet.write('K%s' % row, line['amount_currency'], table_content_style_right_amount_currency)
            else:
                worksheet.write('K%s' % row, line['amount_currency'], table_content_style_right)
            if line['exchange_rate'] != 1:
                worksheet.write('L%s' % row, line['exchange_rate'], table_content_style_right_two_decimal)
            else:
                worksheet.write('L%s' % row, line['exchange_rate'], table_content_style_right)

            worksheet.write('M%s' % row, line['partner'], table_content_style_left_wrap)
            
            row = row + 1
            
        # Footer
        worksheet.merge_range('B{0}:D{0}'.format (row + 3), _('Prepared By'), footer_content_center_bold)
        worksheet.merge_range('B{0}:D{0}'.format (row + 4), _('(Signature, Full Name)'), footer_content_center)
        
        worksheet.merge_range('F{0}:H{0}'.format (row + 3), _('Chief Accountant'), footer_content_center_bold)
        worksheet.merge_range('F{0}:H{0}'.format (row + 4), _('(Signature, Full Name)'), footer_content_center) 
        
        worksheet.merge_range('J{0}:L{0}'.format (row + 2), _('Month ..... Day ..... Year .....'), footer_content_center)
        worksheet.merge_range('J{0}:L{0}'.format (row + 3), _('Director/CEO'), footer_content_center_bold)
        worksheet.merge_range('K{0}:M{0}'.format (row + 4), _('(Signature, Full Name, Job Title)'), footer_content_center)
        
        workbook.close()
        # Back cusor the beginning of the file
        file_data.seek(0)
        return file_data

