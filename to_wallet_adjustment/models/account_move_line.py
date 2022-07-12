from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_wallet_adjustment = fields.Boolean(readonly=True, help="Technical field to indicate if this journal item is a wallet correction item.")
