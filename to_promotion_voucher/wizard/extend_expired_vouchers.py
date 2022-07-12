from odoo import models, fields, api
from datetime import timedelta


class ExtendExpiredVouchers(models.TransientModel):
    _name = 'extend.expired.vouchers'
    _description = "Extend Expried Voucher"

    valid_duration = fields.Integer(string='Valid Duration', required=True,
                                    help='Number of days to extend start counting from today.')
    voucher_ids = fields.Many2many('voucher.voucher', string="Vouchers")

    def action_extend(self):
        for r in self:
            expiry_date = fields.Date.today() + timedelta(days=r.valid_duration)
            r.voucher_ids.write({'state': 'activated', 'expiry_date': expiry_date})
