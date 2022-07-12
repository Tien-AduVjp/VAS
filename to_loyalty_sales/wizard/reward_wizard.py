import math
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RewardWizard(models.TransientModel):
    _name = 'reward.wizard'
    _description = 'Rewards Wizard'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    reward_id = fields.Many2one('loyalty.reward', string='Rewards', required=True)

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        res = {}
        reward_ids = self.sale_order_id.get_available_rewards()
        if reward_ids:
            res['domain'] = {'reward_ids': [('id', 'in', reward_ids.ids)]}
        else:
            res['domain'] = {'reward_ids': []}
        return res

    def action_choose(self):
        self.ensure_one()
        if not self.sale_order_id:
            return {'type': 'ir.actions.act_window_close'}
        # get spendable points
        spendable = self.sale_order_id.get_spendable_points()
        if self.reward_id.minimum_points > spendable:
            raise ValidationError(_("Loyalty points of customer not enough for these rewards."))
        if self.reward_id not in self.sale_order_id.loyalty_id.reward_ids:
            raise ValidationError(_("Loyalty program %s haven't reward %s") % (self.sale_order_id.loyalty_id.name, self.reward_id.name,))
        if self.reward_id.reward_type == 'gift':
            if self.reward_id.point_cost > spendable:
                raise ValidationError(_("The customer's point need bigger than point cost"))
            name = 'Gift'
            price = 0.0
            product_id = self.reward_id.gift_product_id.id
            product_uom = self.reward_id.gift_product_id.uom_id.id,
        elif self.reward_id.reward_type == 'discount':
            prec = self.sale_order_id.loyalty_id._calculate_precision()
            order_total = sum(self.mapped('sale_order_id.order_line.price_subtotal'))

            # calculate discounted amount
            discount = round(order_total * (self.reward_id.discount / 100), 0)

            if round(discount * self.reward_id.point_cost, prec) > spendable:
                discount = round(math.floor(spendable / self.reward_id.point_cost), prec)
            name = _('Max. {0}% Discount').format(self.reward_id.discount)

            price = -discount
            product_id = self.reward_id.discount_product_id.id
            product_uom = self.reward_id.discount_product_id.uom_id.id

        order_lines = self.sale_order_id.order_line.browse([])
        for line in self.sale_order_id.order_line:
            order_lines += line
        new_line = {
            'product_id': product_id,
            'name': name,
            'product_uom_qty': 1,
            'product_uom': product_uom,
            'price_unit': price,
            'reward_id': self.reward_id.id,
            'sequence': 999
        }
        order_lines += order_lines.new(new_line)
        self.sale_order_id.order_line = order_lines
        # After sales order was confirm neew write loyalty points to data base
        if self.sale_order_id.state == 'sale':
            vals = self.sale_order_id.order_line[-1]._prepare_loyalty_point_data()
            self.env['loyalty.point'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
