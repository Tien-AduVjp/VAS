from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    asset_deferral_line_ids = fields.One2many('cost.revenue.deferral.line', 'move_id', string='Deferral Lines', ondelete="restrict")

    def button_cancel(self):
        for move in self:
            for line in move.asset_deferral_line_ids:
                line.move_posted_check = False
        return super(AccountMove, self).button_cancel()

    def post(self):
        for move in self:
            for deferral_line in move.asset_deferral_line_ids:
                deferral_line.post_lines_and_close_deferral()
        return super(AccountMove, self).post()
    