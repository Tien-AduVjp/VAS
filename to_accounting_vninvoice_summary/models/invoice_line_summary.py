from odoo import models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_round


class AccountInvoiceLineGroup(models.Model):
    _inherit = "invoice.line.summary"
    
    def _prepare_vninvoice_line_summary_data(self, sequence=None):
        """
        Hook method for potential inheritance
        """
        self.ensure_one()
        prec = self.env['decimal.precision'].precision_get('Product Price')
        
        data = {
            'index': sequence or self.sequence
            }
        if any([line.display_type for line in self.invoice_line_ids]):
            return False

        # calculate tax
        taxes_count = len(self.invoice_line_tax_ids)

        if taxes_count > 1:
            raise UserError(_("The line containing the product %s comes with more than one tax which is not supported by VN-incoice.\n"
            "You may set some taxes to get their value included in the price to ensure that there is no more than one tax on a single line.")
            % self.product_id.display_name)
        elif taxes_count == 0:
            raise UserError(_("""The line containing the product %s comes with no tax.""") % self.product_id.display_name)
        
        if not self._prepare_einvoice_line_summary_uom_name():
            raise UserError(_("Product %s don't have Unit of measure. VN-Invoice requires Unit of measure in every invoice line") % self._prepare_einvoice_line_name())
            
        # add vat percent for fixed tax
        if float_is_zero(self.price_subtotal, precision_digits=prec):
            vatPercent = 0.0
        else:
            vatPercent = (self.price_total - self.price_subtotal) / self.price_subtotal * 100

        if taxes_count == 1:
            if self.invoice_line_tax_ids.amount_type == 'percent':
                vatPercent = self.invoice_line_tax_ids.amount
            if self.invoice_line_tax_ids.tax_group_id == self.env.ref('l10n_vn_c200.tax_group_exemption'):
                vatPercent = -1
        price_unit = float_round(self.price_unit * (1 - self.discount / 100), precision_digits=prec)
        if self.invoice_line_tax_ids.price_include:
            price_unit = float_round(self.price_unit * (1 - self.discount / 100 ) / (1 + self.invoice_line_tax_ids.amount / 100), precision_digits=prec)
        price_subtotal = self.price_subtotal
        price_total = self.price_total
        if self.invoice_id.invoice_line_summary_mode in ['product_unit_price_tax_discount','product_tax_discount']:
            if self.invoice_id.company_id.einvoice_api_version == 'v1':
                data.update({
                    'productId': self.product_id.default_code or ("PDC_" + str(self.product_id.id)),
                })
            else:
                data.update({
                    'productType': 1,
                    'productCode': self.product_id.default_code or ("PDC_" + str(self.product_id.id)),
                })
        else:
            productName = self.product_tmpl_id.default_code or self.product_tmpl_id.product_variant_id.default_code or self.product_id.default_code or "PDC_" + str(self.product_tmpl_id.id)
            if self.invoice_id.company_id.einvoice_api_version == 'v1':
                data.update({
                    'productId': productName,
                })
            else:
                data.update({
                    'productType': 1,
                    'productCode': productName,
                })
        data.update({
            'productName': self._prepare_einvoice_line_summary_name(),
            'unitName': self._prepare_einvoice_line_summary_uom_name(),
            'unitPrice': float_round(price_unit * (1 - self.discount / 100), precision_digits=prec),
            'quantity': float_round(self.quantity, precision_digits=prec),
            'amount': float_round(price_subtotal, precision_digits=2),
            'vatPercent': int(vatPercent),
            'vatPercentDisplay': self.invoice_line_tax_ids.name,
            'vatAmount': price_total - price_subtotal,
            'note': '',
            'discountAmountBeforeTax': 0.0,
            'discountPercentBeforeTax': 0,
            'paymentAmount': float(price_total)
            })
        return data

    def _prepare_einvoice_line_summary_data(self, sequence=None):
        res = super(AccountInvoiceLineGroup, self)._prepare_einvoice_line_summary_data(sequence)
        if self.invoice_id.company_einvoice_provider == 'vninvoice':
            res = self._prepare_vninvoice_line_summary_data(sequence)
        return res