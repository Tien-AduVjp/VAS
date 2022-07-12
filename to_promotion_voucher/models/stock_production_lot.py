from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    voucher_ids = fields.One2many('voucher.voucher', 'lot_id', string='Vouchers',
                                  groups='to_promotion_voucher.group_promotion_voucher_user',
                                  help="The Vouchers that refer to this lot")

    voucher_id = fields.Many2one('voucher.voucher', string='Voucher', compute='_compute_voucher_id', store=True,
                                 index=True, groups='to_promotion_voucher.group_promotion_voucher_user',
                                 help="The Voucher that refers to this lot for voucher movement tracking.")

    @api.depends('voucher_ids')
    def _compute_voucher_id(self):
        for r in self:
            if r.voucher_ids:
                r.voucher_id = r.voucher_ids[0]
            else:
                r.voucher_id = False

