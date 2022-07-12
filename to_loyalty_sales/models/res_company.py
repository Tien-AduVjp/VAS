from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    loyalty_points_reward_policy = fields.Selection([
        ('order', 'By Ordered quantities'),
#         ('invoiced', 'By Invoiced quantities'),
#         ('delivery', 'By Delivered quantities'),
        ], string='Loyalty Points Reward Policy', default='order',
        required=True,
        help="By Ordered quantities: customers are rewarded with loyalty points as soon as their orders are validated\n"
#         "By Invoiced quantities: loyalty points are rewarded to the customer according to the invoiced quantities\n"
#         "By Delivered quantities: loyalty points are rewarded to the customer according to the delivered quantities\n"
        )
