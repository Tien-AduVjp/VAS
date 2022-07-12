from odoo import api, fields, models, _


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        val = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('refund_original_order_id', False):
            orgin_order = self.env['pos.order'].browse(ui_order['refund_original_order_id'])
            val.update({
                'refund_original_order_id': orgin_order.id,
                'name': orgin_order.name + _(' REFUND'),
                'pos_reference': orgin_order.pos_reference,
            })
        return val
