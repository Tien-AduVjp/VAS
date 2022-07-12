from odoo import fields, models, api

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[
        ('voucher_issue_order', 'Voucher Issue Operation'),
        ('voucher_move_order', 'Voucher Move Operation')],
        ondelete={'voucher_issue_order': 'cascade', 'voucher_move_order': 'cascade'})
    can_create_voucher = fields.Boolean(string="Can Create Voucher", compute='_compute_can_create_voucher', store=True)

    @api.depends('code')
    def _compute_can_create_voucher(self):
        for r in self:
            if r.code == 'voucher_issue_order':
                r.can_create_voucher = True
            else:
                r.can_create_voucher = False
