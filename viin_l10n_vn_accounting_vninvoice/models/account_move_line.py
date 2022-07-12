from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_repr


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_vninvoice_line_data(self, line_data):
        """
        Hook method for potential inheritance
        """
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Product Price')
        data = {
            'index': line_data['lineNumber'],
            'productName': self._prepare_einvoice_line_name(),
        }
        #check if product lines are note or section lines
        if self.display_type:
            if self.move_id.einvoice_api_version == 'v1':
                return False
            else:
                data.update({
                    'productType': 4
                })
                return data

        if self.move_id.move_type == 'out_refund' and not self.reversed_move_line_id:
            raise UserError(_("Invoice line %s is not a reversal of any invoice line") % self.display_name)

        # calculate tax
        taxes_count = len(self.tax_ids)

        if taxes_count > 1:
            raise UserError(_("""The line containing the product %s comes with more than one tax which is not supported by VN-incoice.
            You may set some taxes to get their value included in the price to ensure that there is no more than one tax on a single line.""")
            % self.product_id.display_name)
        elif taxes_count == 0:
            raise UserError(_("""The line containing the product %s comes with no tax.""") % self.product_id.display_name)


        if not self._prepare_einvoice_line_uom_name():
            raise UserError(_("Product %s don't have Unit of measure. VN-Invoice requires Unit of measure in every invoice line") % self._prepare_einvoice_line_name('invoice_line_product'))

        vatPercent = -1 if line_data['vatPercentage'] == -2 else line_data['vatPercentage']

        if taxes_count == 1:
            if self.tax_ids.amount_type == 'percent':
                vatPercent = self.tax_ids.amount
            if self.tax_ids.tax_group_id == self.env.ref('l10n_vn_common.account_tax_group_exemption'):
                vatPercent = -1
        price_unit = float(float_repr(fields.Float.round(self.price_unit * (1 - self.discount / 100), precision_digits=prec), precision_digits=prec))
        if self.tax_ids.price_include:
            price_unit = float(float_repr(fields.Float.round(self.price_unit * (1 - self.discount / 100 ) / (1 + self.tax_ids.amount / 100), precision_digits=prec), precision_digits=prec))
        price_subtotal = self.price_subtotal
        price_total = self.price_total
        quantity = self.quantity
        if self.move_id.move_type == 'out_refund':
            reversed_price_unit = self.reversed_move_line_id.price_unit * (1 - self.reversed_move_line_id.discount / 100)
            if self.reversed_move_line_id.tax_ids.price_include:
                reversed_price_unit = reversed_price_unit / (1 + self.reversed_move_line_id.tax_ids.amount / 100)
            reversed_price_unit = float(float_repr(fields.Float.round(reversed_price_unit, precision_digits=prec), precision_digits=prec))
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
                    )
                )
            if self.move_id.einvoice_api_version == 'v1':
                price_unit = reversed_price_unit - price_unit
                quantity = self.reversed_move_line_id.quantity - quantity
                price_subtotal = self.reversed_move_line_id.price_subtotal - price_subtotal
                price_total = self.reversed_move_line_id.price_total - price_total


        data.update({
            'unitName': line_data['unitName'],
            'unitPrice': price_unit,
            'quantity': quantity,
            'amount': float(float_repr(fields.Float.round(price_subtotal, precision_digits=2), precision_digits=2)),
            'vatPercent': int(vatPercent),
            'vatPercentDisplay': self.tax_ids.with_context(lang=self.env.ref('base.lang_vi_VN').code).name,
            'vatAmount': line_data['vatAmount'],
            'note': self.standardize_einvoice_item_name(self.name) or '',
            'discountAmountBeforeTax': 0.0,
            'discountPercentBeforeTax': 0,
            'paymentAmount': line_data['itemTotalAmountWithVat']
            })
        if self.move_id.einvoice_api_version == 'v1':
            data.update({
                'productId': self.product_id.default_code or ("PDC_" + str(self.product_id.id)),
            })
        else:
            data.update({
                'productType': 1,
                'productCode': self.product_id.default_code or ("PDC_" + str(self.product_id.id)),
            })
        return data
