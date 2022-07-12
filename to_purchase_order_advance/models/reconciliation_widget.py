from odoo import api, models


class ReconciliationWidget(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def _prepare_move_lines(self, move_lines, target_currency=False, target_date=False, recs_count=0):
        ret = super(ReconciliationWidget, self)._prepare_move_lines(move_lines, target_currency, target_date, recs_count)
        MoveLine = self.env['account.move.line']
        for ret_line in ret:
            move_line = MoveLine.browse(ret_line['id'])
            if move_line.payment_id and move_line.payment_id.purchase_order_ids:
                ret_line['purchases_orders_str'] = ', '.join(move_line.payment_id.purchase_order_ids.mapped('name'))
        return ret
