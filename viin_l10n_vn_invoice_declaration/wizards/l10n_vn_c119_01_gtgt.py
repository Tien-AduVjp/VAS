from odoo import models, _
from odoo.tools.misc import format_date

from odoo.exceptions import UserError


class WizardL10n_vn119_01GTGT (models.TransientModel):
    _name = 'wizard.l10n_vn_c119.01gtgt'
    _inherit = 'abstract.l10n_vn_c119.gtgt.wizard'
    _description = 'Vietnam Invoice Declaration sale 01 -1/GTGT Wizard'

    def _get_domain(self):
        """Method use get domain"""
        domain = [('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to),
                  ('type', 'in', ('out_invoice', 'out_refund')), ('state', '=', 'posted')]
        return domain
    
    def _add_content_body(self, moves, content_body):
        Tax = self.env['account.tax']
        tax_sale_vat_exemption_xml_id = 'l10n_vn_c200.%s_tax_sale_vat_exemption' % self.company_id.id
        tax_sale_vat_exemption = self.env.ref(tax_sale_vat_exemption_xml_id, raise_if_not_found=False) or Tax
        taxes = tax_sale_vat_exemption | Tax.search([('is_vat', '=', True)]).sorted(key='amount')
        
        for tax in taxes:
            if tax == tax_sale_vat_exemption:
                if not content_body.get(tax_sale_vat_exemption.name, False):
                    content_body[tax_sale_vat_exemption.name] = []
            else:
                if not content_body.get(tax.amount, False):
                    content_body[tax.amount] = []
            for move in moves.line_ids.filtered(lambda line: tax in line.tax_ids).move_id:
                refund = 1
                if move.type == 'out_refund':
                    refund = -1
                line_taxes = move.line_ids.filtered(lambda line: line.tax_line_id == tax).mapped(lambda line: line.credit + line.debit)
                line_total = move.line_ids.filtered(lambda line: tax in line.tax_ids).mapped(lambda line: line.credit + line.debit)
                vals = (move.legal_number or '', move.invoice_date, move.partner_id.name and move.partner_id.name.capitalize() or '', move.partner_id.vat or '', sum(line_total) * refund, sum(line_taxes) * refund)
                
                if tax == tax_sale_vat_exemption:
                    content_body[tax_sale_vat_exemption.name].append(vals)
                else:
                    content_body[tax.amount].append(vals)
        return content_body

    def export_excel_sale(self):
        """Method Create file Excel"""
        self.ensure_one()
        # Get data
        content_body = self._get_data()
        # Create an new Excel file and add a worksheet and a bold format to use to highlight cells.
        file_data, workbook, worksheet, \
        title_report_format, title_template, interval_format, \
        date_format, currency_format, name_style_format, \
        content_cell_format_center, content_cell_format, content_cell_format_values, \
        content_cell_format_total, content_cell_format_title, name_style_format_footer, \
        name_style_format_title = self._create_file_worksheet()

        # Add data default into file excel
        date_from = format_date(self.env, self.date_from)
        date_to = format_date(self.env, self.date_to)
           
        title_rule = _('Template: 01 -1/GTGT (Released Under the Circular No. 119/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('G1:H2', title_rule, title_template)
        worksheet.merge_range('D3:F3', _('LIST OF INVOICES, FINANCIAL PAPERS OF SOLD GOODS'), title_report_format)
        worksheet.merge_range('D4:F4', _('Date from: %s - Date to: %s') % (date_from, date_to), date_format)
        worksheet.write('G5', _('Currency:'), currency_format)
        worksheet.write('H5', self.company_id.currency_id.name, currency_format)
        # Header_title
        worksheet.merge_range('A6:A7', _('No'), name_style_format)
        worksheet.merge_range('B6:C6', _('Invoice, Bill'), name_style_format)
        worksheet.merge_range('D6:D7', _('Customer'), name_style_format)
        worksheet.merge_range('E6:E7', _('Tax Id'), name_style_format)
        worksheet.merge_range('F6:F7', _('Untaxed Amount'), name_style_format)
        worksheet.merge_range('G6:G7', _('Taxes'), name_style_format)
        worksheet.merge_range('H6:H7', _('Note'), name_style_format)
         
        worksheet.write('B7', _('Invoice No'), name_style_format)
        worksheet.write('C7', _('Date'), name_style_format)
         
        worksheet.write('A8', _('1'), name_style_format)
        worksheet.write('B8', _('2'), name_style_format)
        worksheet.write('C8', _('3'), name_style_format)
        worksheet.write('D8', _('4'), name_style_format)
        worksheet.write('E8', _('5'), name_style_format)
        worksheet.write('F8', _('6'), name_style_format)
        worksheet.write('G8', _('7'), name_style_format)
        worksheet.write('H8', _('8'), name_style_format)
        
        # Insert values into cell content body
        count = 0
        sequence_vat = 1
        untaxed_total = 0
        taxes_total = 0
        for key, values in content_body.items():
            total = 0
            total_tax = 0
            worksheet.set_row(sequence_vat + count + 8, 20)
            tax_sale_vat_exemption_xml_id = 'l10n_vn_c200.%s_tax_sale_vat_exemption' % self.company_id.id
            tax_sale_vat_exemption = self.env.ref(tax_sale_vat_exemption_xml_id, raise_if_not_found=False)
            if tax_sale_vat_exemption and key == tax_sale_vat_exemption.name:
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Exemption Goods & Services') % (sequence_vat,),
                    content_cell_format_title
                    )
            else:
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable Goods & Services %s%s') % (sequence_vat, int(key), '%'),
                    content_cell_format_title
                    )
            sequence = 1
            for row in values:
                worksheet.set_row(sequence_vat + count + 8, 20)
                worksheet.write(sequence_vat + count + 8, 0, sequence, content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 1, row[0], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 2, format_date(self.env, row[1]), content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 3, row[2], content_cell_format)
                worksheet.write(sequence_vat + count + 8, 4, row[3], content_cell_format_center)
                worksheet.write(sequence_vat + count + 8, 5, row[4], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 6, row[5], content_cell_format_values)
                worksheet.write(sequence_vat + count + 8, 7, " ", content_cell_format)
                sequence += 1
                total += row[4]
                total_tax += row[5]
                count += 1
            count += 1
            sequence_vat += 1
            taxes_total += total_tax
            untaxed_total += total
            worksheet.merge_range(
                'A{0}:E{0}'.format(sequence_vat + count + 7),
                _('Total'),
                content_cell_format_title
                )
            worksheet.write(sequence_vat + count + 6, 5, total, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 6, total_tax, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 7, " ", interval_format)

        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 9), _('Untaxed Amount Total (Sales)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 9), untaxed_total, content_cell_format_total)
        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 10), _('Taxes Total (Sales)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 10), taxes_total, content_cell_format_total)
         
        # Footer                                          
        worksheet.merge_range('A{0}:B{0}'.format(sequence_vat + count + 13), _('Prepared By'), name_style_format_title)     
        worksheet.merge_range('A{0}:B{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name)'), name_style_format_footer)
  
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 13), _('Chief Accountant'), name_style_format_title)     
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name)'), name_style_format_footer)        
          
        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 12), _('Month ..... Day ..... Year .....'), name_style_format_footer)
        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 13), _('Director/CEO'), name_style_format_title)     
        worksheet.merge_range('F{0}:H{0}'.format(sequence_vat + count + 14), _('(Signature, Full Name, Job Title)'), name_style_format_footer) 
      
        workbook.close()
        # Back cursor to the beginning of the file
        file_data.seek(0)
        return file_data
        
    def print_sale(self):
        if self.date_from > self.date_to:
            raise UserError(_("The Date From must be less than the Date To."))
        return {
            'type': 'ir.actions.act_url',
            'url': '/invoice-declaration-sales/download/xlsx/%d' % self.id,
            'target': '_blank'
        }
       
