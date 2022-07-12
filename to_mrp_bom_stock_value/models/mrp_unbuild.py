from odoo import models, fields


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    # TODO: remove field when upgrade to 15.0
    consume_move_id = fields.Many2one('stock.move', string='Consume Move')

    def _generate_consume_moves(self):
        moves = super(MrpUnbuild, self)._generate_consume_moves()
        for r in self:
            moves.filtered(lambda m: m.unbuild_id == r).consume_unbuild_id = r
        return moves

    def action_validate(self):
        return super(MrpUnbuild, self.with_context(is_unbuild=True)).action_validate()
