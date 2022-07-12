from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    refund_original_order_id = fields.Many2one('pos.order', string='Return Original',
                                               help="The original order that related to this refund order")

    refund_order_ids = fields.One2many('pos.order', 'refund_original_order_id', string='Return Orders')
    refund_order_count = fields.Integer(string='Return Order Count', compute='_count_refund_order_ids')

    def _count_refund_order_ids(self):
        for r in self:
            r.refund_order_count = len(r.refund_order_ids)

    def refund(self):
        data = super(PosOrder, self).refund()
        order = self.env['pos.order'].browse(data['res_id'])
        order.write({'refund_original_order_id': self.ids[0]})
        return data

    def action_view_refund_orders(self):
        action = self.env.ref('point_of_sale.action_pos_pos_form').read()[0]
        action['domain'] = [('id', 'in', self.refund_order_ids.ids)]
        return action


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    refund_original_line_id = fields.Many2one('pos.order.line', string='Return Original Order Line', help="The original order line that initiate this refund line")
    refund_original_order_id = fields.Many2one('pos.order', string='Return Original Order',
                                               related='order_id.refund_original_order_id', index=True)

    def _prepare_refund_data(self, refund_order_id):
        data = super(PosOrderLine, self)._prepare_refund_data(refund_order_id)
        data['refund_original_line_id'] = self.id
        return data
