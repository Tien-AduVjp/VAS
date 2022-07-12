from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_unit_lock = fields.Boolean(string='Unit Price Lock', compute='_compute_price_unit_lock')

    def _get_vendor_pricelist(self):
        if not self.product_id:
            return False
        vendor_pricelist = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order.date() if self.order_id.date_order else None,
            uom_id=self.product_uom
            )
        return vendor_pricelist

    @api.depends('product_id', 'partner_id')
    def _compute_price_unit_lock(self):
        for r in self:
            price_unit_lock = False
            if r.product_id:
                vendor_pricelist = r._get_vendor_pricelist()
                if vendor_pricelist and vendor_pricelist.state == 'locked':
                    price_unit_lock = True
            r.price_unit_lock = price_unit_lock

    def _get_price(self):
        seller = self._get_vendor_pricelist()

        price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, self.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id._convert(price_unit, self.order_id.currency_id, self.company_id, self.date_order or fields.Date.today())

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        return price_unit

    @api.onchange('price_unit', 'product_uom')
    def _onchange_price_unit(self):
        is_purchase_manager = self.env.user.has_group('purchase.group_purchase_manager')
        prec = self.env['decimal.precision'].precision_get('Product Price')
        if not is_purchase_manager:
            for r in self:
                if r.price_unit_lock and float_compare(r.price_unit, r._get_price(), precision_digits=prec) != 0:
                    raise UserError(_("The pricelist for product \'%s\' from the vendor \'%s\' is currently locked against"
                                         " non purchase manager users."
                                         " Please contact your Purchase Manager in case you want to update the vendor\'s pricelist")
                                         % (r.product_id.name, r.partner_id.name))
