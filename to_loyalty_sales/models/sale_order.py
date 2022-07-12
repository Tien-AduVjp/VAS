from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loyalty_point_ids = fields.One2many('loyalty.point', 'sale_order_id', string='Loyalty Point Entries')
    loyalty_points = fields.Float(string='Loyalty Points', help="The number of Loyalty points the customer won or lost with this order", readonly=True)
    loyalty_id = fields.Many2one('loyalty.program', string='Loyalty Program', compute='_compute_loyalty_id',
                                 store=True, readonly=False, help="The loyalty program used by this sales order."
                                 " A program could be automatically selected here when there is one specified either for the"
                                 " corresponding customer or the sales team.")
    reward_count = fields.Integer(string='Number of Rewards', compute='_compute_loyalty')
    spendable_points = fields.Float(string='Spendable Points', compute='_compute_loyalty')
    customer_level_id = fields.Many2one('customer.level', string='Customer Level')

    @api.depends('team_id', 'partner_id')
    def _compute_loyalty_id(self):
        for r in self:
            r.loyalty_id = self.env['loyalty.program'].find_loyalty_program(r.partner_id, r.team_id)

    @api.depends('order_line', 'loyalty_id')
    def _compute_loyalty(self):
        for r in self:
            if r.loyalty_id:
                r.spendable_points = r.get_spendable_points()
                rewards = self.get_available_rewards()
                r.reward_count = len(rewards)
            else:
                r.spendable_points = 0.0
                r.reward_count = 0

    def action_confirm(self):
        prec = self.env['decimal.precision'].precision_get('Loyalty')

        # generate loyalty points for orders of the companies that have 'Ordered quantities' as the loyalty points reward policy
        for order in self.filtered(lambda so: so.company_id.loyalty_points_reward_policy == 'order'):
            # check
            spent_points = order.get_spent_points()
            if float_compare(spent_points, 0, precision_digits=prec) > 0:
                if float_compare(order.partner_id.loyalty_points, spent_points, precision_digits=prec) < 0:
                    raise ValidationError(_('Loyalty points of customer not enough for these rewards.'))
            order.order_line._generate_loyalty_points()
            order.write({'loyalty_points': self.get_new_points()})
        return super(SaleOrder, self).action_confirm()

    def _prepare_loyalty_point_pp_order_data(self):
        self.ensure_one()

        if not self.loyalty_id:
            return False

        vals = False
        if not float_is_zero(self.loyalty_id.pp_order, precision_rounding=self.loyalty_id.rounding):
            vals = {
                'name': self.name,
                'partner_id': self.partner_id.id,
                'points': float_round(self.loyalty_id.pp_order, precision_rounding=self.loyalty_id.rounding),
                'loyalty_program_id': self.loyalty_id.id,
                'date_order': self.date_order,
                'sale_order_id': self.id,
                'salesperson_id': self.user_id.id,
                'team_id': self.team_id.id,
                'manual_adjustment': False,
            }
        return vals

    def get_won_points(self):
        if not self.loyalty_id or not self.partner_id:
            return 0.0
        total_points = 0.0
        for line in self.order_line:
            total_points += line.get_won_points()
        total_points += float_round(self.loyalty_id.pp_order, precision_rounding=self.loyalty_id.rounding)

        return total_points

    def get_spent_points(self):
        if not self.loyalty_id or not self.partner_id:
            return 0.0
        points = 0.0
        for line in self.order_line:
            points += line.get_spent_points()

        return points

    def get_new_points(self):
        if not self.loyalty_id or not self.partner_id:
            return 0.0
        return float_round(self.get_won_points() - self.get_spent_points(),
                           precision_rounding=self.loyalty_id.rounding)

    def get_current_points(self):
        return self.partner_id and self.partner_id.loyalty_points or 0

    def get_spendable_points(self):
        if not self.loyalty_id or not self.partner_id:
            return 0.0
        spent_points = self.get_spent_points()
        if self.state == 'sale':
            spent_points = 0
        return float_round(self.partner_id.loyalty_points - spent_points,
                           precision_rounding=self.loyalty_id.rounding)

    def get_available_rewards(self):
        if not self.partner_id:
            return []
        rewards = self.env['loyalty.reward']
        for reward in self.loyalty_id.reward_ids:
            if reward.minimum_points > self.get_spendable_points():
                continue
            elif reward.reward_type == 'gift' and reward.point_cost > self.get_spendable_points():
                continue
            rewards += reward
        return rewards

    def action_cancel(self):
        loyalty_point_ids = self.mapped('loyalty_point_ids')
        if loyalty_point_ids:
            loyalty_point_ids.unlink()
        return super(SaleOrder, self).action_cancel()
