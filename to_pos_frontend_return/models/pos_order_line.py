from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _order_line_fields(self, line, session_id=None):
        val = super(PosOrderLine, self)._order_line_fields(line, session_id)
        if line[2].get('refund_original_line_id', False):
            val[2].update({'refund_original_line_id': line[2].get('refund_original_line_id', False)})
        return val
