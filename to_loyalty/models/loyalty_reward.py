from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LoyaltyReward(models.Model):
    _name = 'loyalty.reward'
    _description = 'Loyalty Reward'

    name = fields.Char(index=True, required=True, help='An internal identification for this loyalty reward')
    loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program', help="The Loyalty Program this reward belongs to."
                                         " If empty, this reward is global that can be applied to any loyalty program")
    minimum_points = fields.Float(help='The minimum amount of points the customer must have to qualify for this reward')
    reward_type = fields.Selection([
        ('gift', 'Gift'),
        ('discount', 'Discount')], required=True,
        help="The type of the reward\n"
        "- Gift: The customer spends points to get free Gift. Gift is also a product that you define as the Gift of the reward\n"
        "- Discount: The customer spend points to get discounted.")
    gift_product_id = fields.Many2one('product.product', string='Gift Product', help='The product is given as a reward (aka selling at price of zero)')
    point_cost = fields.Float(string='Point Cost', help="The cost of one point in either the corresponding Loyalty Program's currency"
                              " or the company's currency if the Program does not specify a currency or the reward is global.")
    discount_product_id = fields.Many2one('product.product', string='Discount Product',
                                          help='The product used to apply discounts (aka selling this product at a negative price)')
    discount = fields.Float(help='The discount percentage')

    @api.constrains('reward_type', 'gift_product_id')
    def _check_gift_product(self):
        for r in self:
            if r.reward_type == 'gift' and not r.gift_product_id:
                raise ValidationError(_("The gift product field is mandatory for gift rewards '%s'") % (r.name,))

    @api.constrains('reward_type', 'discount_product_id')
    def _check_discount_product(self):
        for r in self:
            if r.reward_type == 'discount' and not r.discount_product_id:
                raise ValidationError(_("The discount product field is mandatory for discount rewards '%s'") % (r.name,))
