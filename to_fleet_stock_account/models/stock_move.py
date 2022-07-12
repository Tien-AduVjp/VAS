from odoo import models
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        for l in res:
            if not self and not self.id:
                continue
            currency_id = self.env['account.account'].browse(l[2]['account_id']).company_id.currency_id
            if currency_id and not currency_id.is_zero(l[2]['debit']) and self.vehicle_id:
                l[2]['vehicle_ids'] = [(4, self.vehicle_id.id, 0)]
        return res
