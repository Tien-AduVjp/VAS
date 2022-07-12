from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError

class ExtendExpiredVouchers(models.TransientModel):
    _name = 'extend.expired.vouchers'
    _description = "Extend Expried Voucher"

    valid_duration = fields.Integer(string='Valid Duration', required=True,
                                    help='Number of days to extend start counting from today.')
    voucher_ids = fields.Many2many('voucher.voucher', string="Vouchers")

    def action_extend(self):
        for r in self:
            for voucher in r.voucher_ids:
                if voucher.voucher_type_id.payable_once and voucher.used_before:
                    raise  UserError(_("Cannot extend for voucher payable once and used before '%s'", voucher.name))
            r.voucher_ids.write({
                'state': 'activated',
                'activated_date': fields.Date.today(),
                'valid_duration': r.valid_duration
            })
