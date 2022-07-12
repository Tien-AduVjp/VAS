from odoo import models, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class AccountInvoiceLineGroup(models.Model):
    _inherit = "invoice.line.summary"

    def _is_einvoice_deduction_line(self):
        self.ensure_one()
        return self.invoice_id.move_type == 'out_refund'

    def standardize_einvoice_item_name(self, item_name):
        journal = self.invoice_id.journal_id
        if journal.einvoice_item_name_new_line_replacement:
            item_name = item_name.replace("\n", journal.einvoice_item_name_new_line_replacement)
        return item_name

    def _prepare_einvoice_line_summary_uom_name(self):
        """
        Prepare name of UoM in both Vietnamese and English when needed
        """
        if not self.uom_id:
            return ''
        vietnam_lang = self.env.ref('base.lang_vi_VN')
        uom_name = self.uom_id.with_context(lang=vietnam_lang.code).name
        # add English subtitle for foreign customers
        if self.invoice_id._einvoice_need_english():
            us_lang = self.env.ref('base.lang_en')
            uom_name += "\n(%s)" % self.uom_id.with_context(lang=us_lang.code).name
        return uom_name

    def _prepare_einvoice_line_summary_name(self):
        """
        Prepare a string type data for E-Invoice itemName in both Vietnamese and English when needed
        """

        def get_item_name_by_lang(einvoice_item_name, lang):
            if self.invoice_id.invoice_line_summary_group_mode in ['product_unit_price_tax_discount','product_tax_discount']:
                item_name = self.product_id.with_context(lang=lang).name
            else:
                item_name = self.product_tmpl_id.with_context(lang=lang).name
            return item_name

        is_deduction_line = self._is_einvoice_deduction_line()

        # Vietnamese is required by the state so we take the Vietnamese language here for using in context
        vietnam_lang = self.env.ref('base.lang_vi_VN')
        item_name = get_item_name_by_lang(self.invoice_id.journal_id.einvoice_item_name, vietnam_lang.code)
        if is_deduction_line:
            item_name = '[Điều chỉnh giảm] ' + item_name

        # add English subtitle for foreign customers
        if self.invoice_id._einvoice_need_english() and self.product_id:
            us_lang = self.env.ref('base.lang_en')
            item_name += ' '
            if is_deduction_line:
                item_name += '[Deduction Adjustment] '
            item_name += '(%s)' % get_item_name_by_lang(self.invoice_id.journal_id.einvoice_item_name, us_lang.code)
        item_name = self.standardize_einvoice_item_name(item_name)
        return item_name

    def _prepare_einvoice_line_summary_data(self, sequence=None):
        """
        Hook method for potential inheritance
        """
        return {}

    def _prepare_einvoice_summary_lines_data(self):
        move_ids = self.mapped('invoice_id')
        if len(move_ids) > 1:
            raise ValidationError(_("All the invoice lines must belong to the same invoice."))
        data = []
        sequence = 1
        for r in self:
            line = r._prepare_einvoice_line_summary_data(sequence)
            if line:
                data.append(line)
                sequence += 1
        return data
