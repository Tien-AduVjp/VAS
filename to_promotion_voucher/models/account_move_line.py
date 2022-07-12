from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    promotion_voucher_id = fields.Many2one('voucher.voucher', string='Promotion Voucher', readonly=True)

