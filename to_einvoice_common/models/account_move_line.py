from odoo import models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountMoveLine, self)._onchange_product_id()
        if self.journal_id.type == 'sale' and self.move_id.company_einvoice_provider != 'none' and self.product_id:
            name = self.with_context(einvoice_line_name_vi_VN=True,lang='vi_VN')._get_computed_name()
            if self.move_id._einvoice_need_english():
                name += ' (%s)' % self.with_context(lang='en_US', display_default_code=False)._get_computed_name()
            self.standardize_einvoice_item_name(name)
            self.name = name

    def _is_einvoice_deduction_line(self):
        self.ensure_one()
        return self.move_id.type == 'out_refund'

    def _prepare_einvoice_line_uom_name(self):
        """
        Prepare name of UoM in both Vietnamese and English when needed
        """
        if not self.product_uom_id:
            return ''
        vietnam_lang = self.env.ref('base.lang_vi_VN')
        uom_name = self.product_uom_id.with_context(lang=vietnam_lang.code).name
        # add English subtitle for foreign customers
        if self.move_id._einvoice_need_english():
            us_lang = self.env.ref('base.lang_en')
            uom_name += "\n(%s)" % self.product_uom_id.with_context(lang=us_lang.code).name
        return uom_name

    def standardize_einvoice_item_name(self, item_name):
        journal = self.move_id.journal_id
        item_name = item_name.strip()
        if journal.einvoice_item_name_new_line_replacement:
            item_name = item_name.replace("\n", journal.einvoice_item_name_new_line_replacement)
        return item_name

    def _prepare_einvoice_line_name(self, einvoice_item_name=False):
        """
        Prepare a string type data for E-Invoice itemName in both Vietnamese and English when needed
        """

        def get_item_name_by_lang(einvoice_item_name, lang):
            if einvoice_item_name == 'invoice_line_product' and self.product_id:
                item_name = self.product_id.with_context(lang=lang).name
            else:
                item_name = self.with_context(lang=lang).name
            return item_name

        is_deduction_line = self._is_einvoice_deduction_line()
        item_name = ''
        if not einvoice_item_name:
            einvoice_item_name = self.move_id.journal_id.einvoice_item_name
        # get product description for item name
        if einvoice_item_name == 'invoice_line_name':
            return self.standardize_einvoice_item_name(self.name)
    
        # Vietnamese is required by the state so we take the Vietnamese language here for using in context
        vietnam_lang = self.env.ref('base.lang_vi_VN')
        item_name = get_item_name_by_lang(einvoice_item_name, vietnam_lang.code)
        if is_deduction_line:
            item_name = '[Điều chỉnh giảm] ' + item_name

        # add English subtitle for foreign customers
        if self.move_id._einvoice_need_english() and self.product_id:
            us_lang = self.env.ref('base.lang_en')
            item_name += ' '
            if is_deduction_line:
                item_name += '[Deduction Adjustment] '
            item_name += '(%s)' % get_item_name_by_lang(einvoice_item_name, us_lang.code)
        item_name = self.standardize_einvoice_item_name(item_name)
        return item_name

    def _prepare_einvoice_line_data(self, sequence=None):
        """
        Hook method for potential inheritance
        """
        self.ensure_one()
        if not self.display_type and self.move_id.type == 'out_refund' and not self.reversed_move_line_id:
            raise UserError(_("Adjustment Line %s is not a reversal of any original invoice line") % (self.name))
        return {}

    def _prepare_einvoice_lines_data(self):
        move_ids = self.mapped('move_id')
        if len(move_ids) > 1:
            raise ValidationError(_("All the invoice lines must belong to the same invoice."))
        data = []
        sequence = 1
        # Odoo does not respect sequence at Python level. It applies sequence on invoice form view only.
        # So, sorted is required to ensure sequence is respected to reflect ordering consistance between
        # invoice form view and einvoice
        for r in self.sorted(lambda line: (line.sequence, line.id)):
            line = r._prepare_einvoice_line_data(sequence)
            if line:
                data.append(r._prepare_einvoice_line_data(sequence))
                sequence += 1
        return data
