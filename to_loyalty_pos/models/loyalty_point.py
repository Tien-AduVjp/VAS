from odoo import fields, models

class LoyaltyPoint(models.Model):
    _inherit = 'loyalty.point'

    pos_order_line_id = fields.Many2one('pos.order.line', string='POS Order Line', index=True)
    pos_order_id = fields.Many2one('pos.order', string='PoS Order', index=True)
    session_id = fields.Many2one('pos.session', string='PoS Session', related='pos_order_id.session_id', store=True, index=True)
