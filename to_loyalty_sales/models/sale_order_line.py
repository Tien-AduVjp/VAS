from odoo import fields, models, api
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_round


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    reward_id = fields.Many2one('loyalty.reward', string='Reward', readonly=True, help="This field is to indicate that the line is a reward line")
    loyalty_points = fields.Float(string='Loyalty Points', help="The number of Loyalty points the customer won or lost with this order line", readonly=True,
                                  digits='Loyalty',
                                  compute='_compute_loyalty_points', store=True)
    # loyalty.point One2one sale.order.line
    loyalty_point_ids = fields.One2many('loyalty.point', 'sale_order_line_id', string='Loyalty Point', readonly=True)

    @api.depends('product_id', 'product_uom_qty', 'product_uom',
                 'price_subtotal', 'currency_id',
                 'order_id.loyalty_id',
                 'qty_delivered', 'qty_invoiced')
    def _compute_loyalty_points(self):
        for r in self:
            r.loyalty_points = r.get_new_points()
            if r.order_id.state == 'sale' and r.loyalty_point_ids:
                r.loyalty_point_ids.points = r.loyalty_points

    def get_won_points(self):
        if self.order_id.loyalty_id and self.order_id.partner_id and not self.reward_id:
            won_points = self.order_id.loyalty_id.calculate_won_points(
                company_id=self.company_id or self.order_id.company_id,
                product_id=self.product_id,
                product_qty=self.product_uom_qty,
                price_subtotal=self.price_subtotal,  # Without taxes
                product_uom=self.product_uom,
                currency_id=self.currency_id,
                date=self.order_id.date_order
            )
        # return zero if the line is either a reward line
        # or a no loyalty program line
        # or a no partner line
        else:
            won_points = 0.0
        return won_points

    def get_spent_points(self):
        if not self.order_id.loyalty_id or not self.order_id.partner_id or not self.reward_id:
            spent_points = 0.0
        else:
            spent_points = self.order_id.loyalty_id.calculate_spent_points(
                company_id=self.company_id,
                product_id=self.product_id,
                product_qty=self.product_uom_qty,
                price_subtotal=self.price_subtotal,
                reward_id=self.reward_id,
                product_uom=self.product_uom,
                currency_id=self.currency_id,
                date=self.order_id.date_order
            )
        return spent_points

    def get_new_points(self):
        if not self.order_id.loyalty_id or not self.order_id.partner_id:
            return 0.0
        return float_round(self.get_won_points() - self.get_spent_points(),
                           precision_rounding=self.order_id.loyalty_id.rounding)

    def _prepare_loyalty_point_data(self):
        data = {
            'name': self.order_id.name,
            'partner_id': self.order_id.partner_id.id,
            'points': self.loyalty_points,
            'sale_order_line_id': self.id,
            'loyalty_program_id': self.order_id.loyalty_id.id,
            'product_id': self.product_id.id,
            'product_qty': self.product_uom_qty,
            'price_total': self.price_subtotal,
            'date_order': self.order_id.date_order,
            'salesperson_id': self.order_id.user_id.id,
            'team_id': self.order_id.team_id.id,
            'manual_adjustment': False,
        }
        if self.reward_id:
            data['reward_id'] = self.reward_id.id
        return data

    def _generate_loyalty_points(self):
        prec = self.env['decimal.precision'].precision_get('Loyalty')

        vals_list = []
        for r in self:
            if not float_is_zero(r.loyalty_points, precision_digits=prec):
                data = r._prepare_loyalty_point_data()
                vals_list.append(data)

        for order in self.mapped('order_id'):
            vals = order._prepare_loyalty_point_pp_order_data()
            if vals:
                vals_list.append(vals)

        if vals_list:
            self.env['loyalty.point'].create(vals_list)
