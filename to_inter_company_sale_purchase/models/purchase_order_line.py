from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    inter_comp_sale_order_line_id = fields.Many2one('sale.order.line', string='Inter-Company Sale Order Line', readonly=True, copy=False)

    def _prepare_inter_comp_sale_order_line_data(self, sale_order):
        """
        Generate the Sales Order Line values from the PO line
        """
        partner = self.partner_id or self.order_id.partner_id
        company = partner._find_company()
        # it may not affected because of parallel company relation
        price = self.price_unit or 0.0
        taxes = self.taxes_id
        if self.product_id:
            taxes = self.product_id.taxes_id
        company_taxes = [tax_rec for tax_rec in taxes if tax_rec.company_id.id == company.id]
        if sale_order:
            company_taxes = sale_order.fiscal_position_id.map_tax(company_taxes, self.product_id, sale_order.partner_id)
        quantity = self.product_id and self.product_uom._compute_quantity(self.product_qty, self.product_id.uom_id) or self.product_qty
        price = self.product_id and self.product_uom._compute_price(price, self.product_id.uom_id) or price
        return {
            'name': self.name,
            'order_id': sale_order.id,
            'product_uom_qty': quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom': self.product_id and self.product_id.uom_id.id or self.product_uom.id,
            'price_unit': price,
            'company_id': company.id,
            'tax_id': [(6, 0, company_taxes.ids)],
            'inter_comp_purchase_order_line_id': self.id
        }
