from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    return_reason_id = fields.Many2one('product.return.reason', string='Return Reason', ondelete='restrict')

    def _order_line_fields(self, line, session_id=None):
        val = super(PosOrderLine, self)._order_line_fields(line, session_id)
        return_reason_id = line[2].get('return_reason_id', False)
        if return_reason_id and return_reason_id != '':
            if return_reason_id != '-1':
                val[2].update({'return_reason_id': return_reason_id})
            else:
                return_reason_orther = line[2].get('return_reason_orther', False)
                if return_reason_orther:
                    new_reason = self.env['product.return.reason'].create({
                        'name': return_reason_orther
                    })
                    val[2].update({'return_reason_id': new_reason.id})
        return val
