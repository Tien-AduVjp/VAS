from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    reversed_move_line_ids = fields.One2many(related='move_id.reversed_entry_id.invoice_line_ids')
    reversed_move_line_id = fields.Many2one('account.move.line', string="Reversal of", copy=False,
                                            domain="[('id', '=', reversed_move_line_ids)]")

    def _copy_data_extend_business_fields(self, values):
        super(AccountMoveLine, self)._copy_data_extend_business_fields(values)
        if 'move_reverse_cancel' in self._context and not self.exclude_from_invoice_tab:
            values['reversed_move_line_id'] = self.id
