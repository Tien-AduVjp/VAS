from odoo import models, _
from odoo.tools.misc import format_date

from odoo.exceptions import UserError


class WizardL10n_vn119_02GTGT (models.TransientModel):
    _name = 'wizard.l10n_vn_c119.02gtgt'
    _inherit = 'abstract.l10n_vn_c119.gtgt.wizard'
    _description = 'Vietnam Invoice Declaration purchase 01 -2/GTGT Wizard'
                
    def _get_domain(self):
        """Method use get domain"""
        domain = [('invoice_date', '>=', self.date_from), ('invoice_date', '<=', self.date_to),
                  ('type', 'in', ('in_invoice', 'in_refund')), ('state', '=', 'posted')]
        return domain 

    def _add_content_body(self, moves, content_body):
        tags = self.env['account.analytic.tag']
        tags |= self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_taxable', raise_if_not_found=False) or tags
        tags |= self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_exemption', raise_if_not_found=False) or tags
        tags |= self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_vat_taxable_and_exemption', raise_if_not_found=False) or tags
        tags |= self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_goods_and_services_investment_projects', raise_if_not_found=False) or tags
        
        for tag in tags:
            if not content_body.get(tag, False):
                content_body[tag] = []
            for move in moves.line_ids.filtered(lambda line: tag in line.analytic_tag_ids and line.tax_ids).move_id:
                for tax in move.line_ids.tax_ids:
                    refund = 1
                    if move.type == 'in_refund':
                        refund = -1
                    line_taxes = move.line_ids.filtered(lambda line: line.tax_line_id == tax and tag in line.analytic_tag_ids).mapped(lambda line: line.credit + line.debit)
                    line_total = move.line_ids.filtered(lambda line: tax in line.tax_ids and tag in line.analytic_tag_ids).mapped(lambda line: line.credit + line.debit)
                    if line_total:
                        vals = (move.legal_number or '', move.invoice_date, move.partner_id.name and move.partner_id.name.capitalize() or '', move.partner_id.vat or '', sum(line_total) * refund, sum(line_taxes) * refund)
                        content_body[tag].append(vals)
        return content_body

    def export_excel_purchase(self):
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
          
        title_rule = _('Template: 01 -2/GTGT (Released Under the Circular No. 119/2014/TT-BTC Dated 22/12/2014 by the Ministry of Finance)')
        worksheet.merge_range('G1:H2', title_rule, title_template)
        worksheet.merge_range('D3:F3', _('LIST OF INVOICES, FINANCIAL PAPERS OF PURCHASED GOODS AND SERVICES'), title_report_format)
        worksheet.merge_range('D4:F4', _('Date from: %s - Date to: %s') % (date_from, date_to), date_format)
        worksheet.write('G5', _('Currency:'), currency_format)
        worksheet.write('H5', self.company_id.currency_id.name, currency_format)
        # Header_title
        worksheet.merge_range('A6:A7', _('No'), name_style_format)
        worksheet.merge_range('B6:C6', _('Invoice, Bill'), name_style_format)
        worksheet.merge_range('D6:D7', _('Vendor'), name_style_format)
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
            sequence = 1
            total_tax = 0
            total = 0
            worksheet.set_row(sequence_vat + count + 8, 20)
            if key == self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_taxable'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable Goods & Services for Production and Business be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif key == self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_exemption'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Exemption Goods & Services for Production and Business') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif key == self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_vat_taxable_and_exemption'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. VAT Taxable and Exemption Goods & Services for Production and Business be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )
            elif key == self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_goods_and_services_investment_projects'):
                worksheet.merge_range(
                    'A{0}:H{0}'.format(sequence_vat + count + 8),
                    _('%s. Goods & Services for Investment Projects be eligible for VAT deduction') % (sequence_vat,),
                    content_cell_format_title
                    )           
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
            worksheet.merge_range('A{0}:E{0}'.format(sequence_vat + count + 7), _('Total'), content_cell_format_title)
            if key == self.env.ref('viin_l10n_vn_invoice_declaration.analytic_tag_vat_exemption'):
                worksheet.write_comment('G{0}'.format(sequence_vat + count + 7), _('is a summary of non-deductible tax'))
            worksheet.write(sequence_vat + count + 6, 5, total, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 6, total_tax, content_cell_format_total)
            worksheet.write(sequence_vat + count + 6, 7, " ", interval_format)
        
        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 9), _('Untaxed Amount Total (Purchase)'), content_cell_format_title)
        worksheet.merge_range('D{0}:E{0}'.format(sequence_vat + count + 9), untaxed_total, content_cell_format_total)
        worksheet.merge_range('A{0}:C{0}'.format(sequence_vat + count + 10), _('Taxes Total (Purchase)'), content_cell_format_title)
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
        
    def print_purchase(self):
        if self.date_from > self.date_to:
            raise UserError(_("The Date From must be less than the Date To."))
        return {
            'type': 'ir.actions.act_url',
            'url': '/invoice-declaration-purchase/download/xlsx/%d' % self.id,
            'target': '_blank'
        }
