from odoo import api, models, _
from odoo.fields import Float
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_repr


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountMoveLine, self)._onchange_product_id()
        if self.journal_id.type == 'sale' and self.move_id.einvoice_provider != 'none' and self.product_id:
            self.product_id.invalidate_cache(['partner_ref'], [self.product_id.id])
            name = self.with_context(einvoice_line_name_vi_VN=True,lang='vi_VN')._get_computed_name()
            if self.move_id._einvoice_need_english():
                name += ' (%s)' % self.with_context(lang='en_US', display_default_code=False)._get_computed_name()
            self.standardize_einvoice_item_name(name)
            self.name = name

    def _is_einvoice_deduction_line(self):
        return self.move_id.move_type == 'out_refund'

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
            res = r._prepare_einvoice_line_data(sequence)
            method = '_prepare_%s_line_data' % self.move_id.einvoice_provider
            if hasattr(r, method) and not self._context.get('edi_vn_xml', False):
                res = getattr(r, method)(res)
            if res:
                data.append(res)
                sequence += 1
        return data

    def _prepend_vietnamese_description_to_name(self):
        for r in self.filtered(lambda line: line.product_id).with_context(lang=self.env.ref('base.lang_vi_VN').code):
            new_invoice_line_name = r.product_id.description_sale or r.product_id.name
            new_invoice_line_name += ' (%s)' % r.name
            r.name = r.standardize_einvoice_item_name(new_invoice_line_name)

    def _prepare_einvoice_line_data(self, sequence):
        self.ensure_one()
        if not self.display_type and self.move_id.move_type == 'out_refund' and not self.reversed_move_line_id:
            raise UserError(_("Adjustment Line %s is not a reversal of any original invoice line") % (self.name))
        prec = self.env['decimal.precision'].precision_get('Product Price')
        data = {
            'lineNumber': sequence,
            'selection': 1,
        }
        if self.display_type:
            data.update({
                'selection': 2,
                'itemName': self.name
            })
        else:
            # check item name limit
            if len(self._prepare_einvoice_line_name().encode(
                    'utf8')) > self.move_id.journal_id.einvoice_item_name_limit:
                raise UserError(
                    _("It seems that your product name/description in invoice lines was too long for E-Invoice."
                      " You should shorten your product name/description to less than %s characters") %
                    self.move_id.journal_id.einvoice_item_name_limit)

            # calculate tax
            taxes_count = len(self.tax_ids)
            if taxes_count > 1:
                raise UserError(_("The line containing the product %s comes with more than one tax which is not supported by E-Invoice. "
                        "You may set some taxes to get their value included in the price to ensure that there is no more than one tax on a single line.")
                                % self.product_id.display_name)
            elif taxes_count == 0:
                raise UserError(
                    _("""The line containing the product %s comes with no tax.""") % self.product_id.display_name)

            if Float.is_zero(self.price_subtotal, precision_digits=prec):
                taxPercentage = 0.0
            else:
                taxPercentage = (self.price_total - self.price_subtotal) / self.price_subtotal * 100

            if taxes_count == 1:
                if self.tax_ids.amount_type == 'percent':
                    taxPercentage = self.tax_ids.amount
                else:
                    raise UserError(
                        _("The line containing the product %s comes with tax has 'Tax Computation' is not 'Percentage of Price' which is not "
                          "supported by E-Invoice.You may set some taxes to get their value included in the price to ensure that their 'Tax Computation' is 'Percentage of Price'.")
                        % self.product_id.display_name)
                exemption_group = self.env.ref('l10n_vn_common.account_tax_group_exemption').id
                if self.tax_ids.tax_group_id.id == exemption_group:
                    taxPercentage = -2

            price_unit = float(float_repr(Float.round(self.price_unit * (1 - self.discount / 100), precision_digits=prec), precision_digits=prec))
            if self.tax_ids.price_include:
                price_unit = float(float_repr(Float.round(self.price_unit * (1 - self.discount / 100) / (1 + self.tax_ids.amount / 100),
                                         precision_digits=prec), precision_digits=prec))

            quantity = abs(self.quantity)
            price_subtotal = abs(self.price_subtotal)
            price_total = abs(self.price_total)

            data.update({
                'itemName': self._prepare_einvoice_line_name(),
                'unitName': self._prepare_einvoice_line_uom_name(),
                'itemCode': self.product_id.default_code or '',
                'unitPrice': price_unit,
                'quantity': quantity,
                'itemTotalAmountWithoutVat': price_subtotal,
                'vatPercentage': taxPercentage,
                'vatAmount': float(float_repr(self.move_id.currency_id.round(price_total - price_subtotal), precision_digits=self.move_id.currency_id.decimal_places)),
                'itemTotalAmountWithVat': price_total,

            })
        return data
