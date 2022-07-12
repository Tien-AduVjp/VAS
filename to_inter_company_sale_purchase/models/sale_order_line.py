from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    inter_comp_purchase_order_line_id = fields.Many2one('purchase.order.line', string='Inter-Company Purchase Order Line', readonly=True, copy=False)

    def _prepare_inter_comp_purchase_order_line_data(self, date_order, purchase_order, company):
        """ Generate purchase order line values, from the SO line
        """
        # price on PO so_line should be so_line - discount
        price = self.price_unit - (self.price_unit * (self.discount / 100))

        # computing Default taxes of so_line. It may not affect because of parallel company relation
        taxes = self.tax_id
        if self.product_id:
            taxes = self.product_id.supplier_taxes_id

        # fetch taxes by company not by inter-company user
        company_taxes = taxes.filtered(lambda t: t.company_id == company)
        if purchase_order:
            company_taxes = purchase_order.fiscal_position_id.map_tax(company_taxes, self.product_id, purchase_order.partner_id)

        quantity = self.product_id and self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_po_id) or self.product_uom_qty
        price = self.product_id and self.product_uom._compute_price(price, self.product_id.uom_po_id) or price
        return {
            'name': self.name,
            'order_id': purchase_order.id,
            'product_qty': quantity,
            'product_id': self.product_id and self.product_id.id or False,
            'product_uom': self.product_id and self.product_id.uom_po_id.id or self.product_uom.id,
            'price_unit': price or 0.0,
            'company_id': company.id,
            'date_planned': self.order_id.expected_date or date_order,
            'taxes_id': [(6, 0, company_taxes.ids)],
            'inter_comp_sale_order_line_id': self.id
        }
