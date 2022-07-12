from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LoyaltyPoint(models.Model):
    _name = 'loyalty.point'
    _description = 'Loyalty Point'

    name = fields.Char(string='Reference')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, index=True)
    loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program', help='The Loyalty Program this customer used', required=True, index=True)
    points = fields.Float(string='Points', digits='Loyalty', help='The loyalty points the user won or lost as part of a Loyalty Program', required=True, index=True)
    reward_id = fields.Many2one('loyalty.reward', string='Loyalty Reward', help='The Loyalty Reward this customer used')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Product Q\'ty', help='The quantity of product in Default Product UoM')
    price_total = fields.Float(string='Price Total', help="The price in the corresponding order's currency")
    date_order = fields.Datetime(string='Date Order', default=fields.Datetime.now)
    reason = fields.Text(string='Reason')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', index=True)
    team_id = fields.Many2one('crm.team', string='Sales Channel', help="The sales team / channel that recorded this loyalty points")
    manual_adjustment = fields.Boolean(string='Manual Adjustment', default=True, help="This field is to indicate if this point is manually created"
                                       " (e.g. created during manual loyalty points adjustment)")

    @api.constrains('manual_adjustment', 'product_id')
    def _check_manual_adjustment_vs_product(self):
        for r in self:
            if r.manual_adjustment and r.product_id:
                raise ValidationError(_("Manual Adjustment must not have the product specified"))

    @api.constrains('manual_adjustment', 'reward_id')
    def _check_manual_adjustment_vs_reward(self):
        for r in self:
            if r.manual_adjustment and r.reward_id:
                raise ValidationError(_("Manual Adjustment must not have the reward specified"))
