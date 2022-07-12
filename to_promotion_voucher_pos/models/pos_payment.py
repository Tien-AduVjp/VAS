from odoo import fields, models


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    voucher_id = fields.Many2one('voucher.voucher', string="Promotion Voucher", ondelete='cascade')
