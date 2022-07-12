from odoo import fields, models
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    affcode_id = fields.Many2one(related='order_id.affcode_id', store=True)
    commission_line_ids = fields.One2many('affiliate.commission.line', 'sale_order_line_id', string='Commission Lines', readonly=True)
    
    def _prepare_invoice_line(self):
        """
        override to pass affcode_id from sales order line to invoice lines to record customer invoice line that related to affiliate sales
        """
        self.ensure_one()
        vals = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.affcode_id:
            vals.update({
                'affcode_id': self.affcode_id.id,
                'commission_line_id': self.commission_line_ids and self.commission_line_ids[0].id or False
                })
        return vals

    def _prepare_commission_line_data(self):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Price')
        affiliate_comm_percentage, rule = self.affcode_id._get_comm_percentage(self.product_id)
        if not float_is_zero(affiliate_comm_percentage, precision_digits=precision):
            return {
                'sale_order_line_id': self.id,
                'affiliate_commission_rule_id': rule.id,
                'product_id': self.product_id.id,
                'currency_id': self.currency_id.id,
                'affiliate_comm_percentage': affiliate_comm_percentage,
                }
        return {}
