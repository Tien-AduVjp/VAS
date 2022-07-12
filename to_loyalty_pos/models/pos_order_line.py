from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    loyalty_points = fields.Float(string='Loyalty Points', digits='Loyalty', readonly=True,
                                  help="The amount of Loyalty points the customer won or lost with this order line")
    refund_points = fields.Float(help='The amount of Loyalty points the customer lost with refund', compute='_compute_loyalty_points', store=True)
    reward_id = fields.Many2one('loyalty.reward', string='Reward', readonly=True, help="This field is to indicate that the line is a reward line")
    loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program')
    price_total = fields.Float(string='Price', related='price_subtotal', store=True)

    @api.depends('product_id', 'qty', 'price_subtotal', 'order_id.refund_original_order_id')
    def _compute_loyalty_points(self):
        for r in self:
            if r.order_id.refund_original_order_id:
                r.refund_points = r.get_new_points()

    def get_won_points(self):
        if self.order_id.config_id.loyalty_id and self.order_id.partner_id and not self.reward_id:
            won_points = self.order_id.config_id.loyalty_id.calculate_won_points(
                company_id=self.company_id,
                product_id=self.product_id,
                product_qty=self.qty,
                price_subtotal=self.price_subtotal,  # Without taxes
                product_uom=None,  # PoS line does not have UoM
                currency_id=self.order_id.config_id.currency_id,
                date=self.order_id.date_order
            )
        # return zero if the line is either a reward line
        # or a no loyalty program line
        # or a no partner line
        else:
            won_points = 0.0
        return won_points

    def get_spent_points(self):
        if not self.order_id.config_id.loyalty_id or not self.order_id.partner_id or not self.reward_id:
            spent_points = 0.0
        else:
            spent_points = self.order_id.config_id.loyalty_id.calculate_spent_points(
                company_id=self.company_id,
                product_id=self.product_id,
                product_qty=self.qty,
                price_subtotal=self.price_subtotal,
                reward_id=self.reward_id,
                product_uom=None,  # PoS line does not have UoM
                currency_id=self.order_id.config_id.currency_id,
                date=self.order_id.date_order
            )
        return spent_points

    def get_new_points(self):
        if not self.order_id.config_id.loyalty_id or not self.order_id.partner_id:
            return 0.0
        return round(self.get_won_points() - self.get_spent_points(), precision_rounding=self.order_id.config_id.loyalty_id.rounding)

    @api.model
    def _prepare_loyalty_point_data(self):
        data = {
            'name': self.order_id.name,
            'partner_id': self.order_id.partner_id.id,
            'points': self.loyalty_points,
            'pos_order_line_id': self.id,
            'pos_order_id': self.order_id.id,
            'loyalty_program_id': self.loyalty_program_id.id,
            'product_id': self.product_id.id,
            'product_qty': self.qty,
            'price_total': self.price_subtotal,
            'date_order': self.order_id.date_order,
            'salesperson_id': self.order_id.user_id.id,
            'manual_adjustment': False,
        }
        if self.reward_id:
            data['reward_id'] = self.reward_id.id
        return data
