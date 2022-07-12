from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_round


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    def _prepare_sinvoice_line_data(self, sequence=None):
        """
        Hook method for potential inheritance
        """
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Product Price')
        data = {
            'lineNumber': sequence or self.sequence
            }
        if self.display_type:
            data.update({
                'selection': 2,
                'itemName': self.name
                })
        else:
            
            #check item name limit
            if len(self._prepare_einvoice_line_name().encode('utf8')) > self.move_id.journal_id.einvoice_item_name_limit:
                raise UserError(_("It seems that your product name/description in invoice lines was too long for SInvoice. You should shorten your product name/description to less than %s characters") % self.move_id.journal_id.einvoice_item_name_limit)

            # calculate tax
            taxes_count = len(self.tax_ids)
            if taxes_count > 1:
                raise UserError(_("""The line containing the product %s comes with more than one tax which is not supported by S-Invoice.
                You may set some taxes to get their value included in the price to ensure that there is no more than one tax on a single line.""")
                % self.product_id.display_name)
            elif taxes_count == 0:
                raise UserError(_("""The line containing the product %s comes with no tax.""") % self.product_id.display_name)

            if float_is_zero(self.price_subtotal, precision_digits=prec):
                taxPercentage = 0.0
            else:
                taxPercentage = (self.price_total - self.price_subtotal) / self.price_subtotal * 100

            if taxes_count == 1:
                if self.tax_ids.amount_type == 'percent':
                    taxPercentage = self.tax_ids.amount
                else:
                    raise UserError(_("The line containing the product %s comes with tax has 'Tax Computation' is not 'Percentage of Price' which is not "
                    "supported by S-Invoice.You may set some taxes to get their value included in the price to ensure that their 'Tax Computation' is 'Percentage of Price'.")
                    % self.product_id.display_name)
                exemption_group = self.env.ref('l10n_vn_c200.tax_group_exemption').id
                if self.tax_ids.tax_group_id.id == exemption_group:
                    taxPercentage = -2

            data.update({
                'itemName': self._prepare_einvoice_line_name(),
                'unitName': self._prepare_einvoice_line_uom_name()
                })
            price_unit = float_round(self.price_unit * (1 - self.discount / 100), precision_digits=prec)
            if self.tax_ids.price_include:
                price_unit = float_round(self.price_unit * (1 - self.discount / 100 ) / (1 + self.tax_ids.amount / 100), precision_digits=prec)
            # S-Invoice does not accept negative quantity while Odoo does
            quantity = abs(self.quantity)
            # S-Invoice does not accept negative Untaxed Subtotal while Odoo does
            price_subtotal = abs(self.price_subtotal)
            # S-Invoice does not accept negative Taxed Subtotal while Odoo does
            price_total = abs(self.price_total)
            if self.product_id.default_code:
                data.update({'itemCode': self.product_id.default_code})
            if self.move_id.type == 'out_refund':
                reversed_price_unit = self.reversed_move_line_id.price_unit * (1 - self.reversed_move_line_id.discount / 100)
                if self.reversed_move_line_id.tax_ids.price_include:
                    reversed_price_unit = reversed_price_unit / (1 + self.reversed_move_line_id.tax_ids.amount / 100)
                reversed_price_unit = float_round(reversed_price_unit, precision_digits=prec)
                if reversed_price_unit < price_unit:
                    raise UserError(
                        _("price unit %s of line %s must not greater than price unit %s of invoice line %s of original invoice %s")
                        % (
                            price_unit,
                            self.display_name,
                            reversed_price_unit,
                            self.reversed_move_line_id.display_name,
                            self.move_id.reversed_entry_id.display_name
                        ))
                if self.reversed_move_line_id.quantity < quantity:
                    raise UserError(
                        _("quantity %s of line %s must not greater than quantity %s of invoice line %s of original invoice %s")
                        % (
                            quantity,
                            self.display_name,
                            self.reversed_move_line_id.quantity,
                            self.reversed_move_line_id.display_name,
                            self.move_id.reversed_entry_id.display_name
                        ))
            data.update({
                'unitPrice': price_unit,
                'quantity': quantity,
                'itemTotalAmountWithoutTax': price_subtotal,
                'taxPercentage': taxPercentage,
                'taxAmount': self.move_id.currency_id.round(price_total - price_subtotal),
                'discount': 0,
                'itemDiscount': 0,
                'itemTotalAmountWithTax': price_total
                })
            if self.move_id.type == 'out_refund':
                data.update({
                    'adjustmentTaxAmount': self.move_id.currency_id.round(price_total - price_subtotal),
                    'isIncreaseItem': False,
                    'itemTotalAmountAfterDiscount': price_total
                })
        return data

    def _prepare_einvoice_line_data(self, sequence=None):
        res = super(AccountMoveLine, self)._prepare_einvoice_line_data(sequence)
        if self.move_id.company_einvoice_provider == 'sinvoice':
            res = self._prepare_sinvoice_line_data(sequence)
        return res

