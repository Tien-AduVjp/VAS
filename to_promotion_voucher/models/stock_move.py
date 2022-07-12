from odoo import fields, models, _
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    order_id = fields.Many2one('voucher.issue.order', string='Voucher Issue Order')
    move_order_id = fields.Many2one('voucher.move.order', string='Voucher Move Order')
    give_order_id = fields.Many2one('voucher.give.order', string='Voucher Give Order')

    def validate_promotion_voucher_move(self, lot_ids=False):
        self.ensure_one()
        if lot_ids and len(self.move_line_ids) != len(lot_ids):
            raise ValidationError(_('Quantity of vouchers not match.'))
        i = 0
        for line in self.move_line_ids:
            line.write({
                'qty_done': 1,
                'lot_id': lot_ids and lot_ids[i].id or line.lot_id and line.lot_id.id or False
                })
            i += 1

    def _action_assign(self):
        super(StockMove, self)._action_assign()
        StockProductionLot = self.env['stock.production.lot']
        for line in self.move_line_ids:
            if line.product_id.is_promotion_voucher and line.move_id.picking_type_id and line.move_id.picking_type_id.can_create_voucher:
                lot_id = StockProductionLot.create({'product_id': line.product_id.id, 'company_id': line.company_id.id})
                line.create_promotion_voucher(lot_id)
                line.write({'lot_id': lot_id.id, 'qty_done': 1})

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)
        vouchers_in_customer = self.move_line_ids.sudo().voucher_id.filtered(lambda x: x.current_stock_location_id.usage == 'customer')
        vouchers_in_customer.write({
            'state': 'activated',
            'activated_date': fields.Date.today()
            })
        return res

