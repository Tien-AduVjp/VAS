from odoo import fields, models


class LoyaltyRule(models.Model):
    _name = 'loyalty.rule'
    _description = 'Loyalty Rule'

    name = fields.Char(index=True, required=True, help="An internal identification for this loyalty program rule")
    loyalty_program_id = fields.Many2one('loyalty.program', string='Loyalty Program', help='The Loyalty Program to which this loyalty rule belongs')
    rule_type = fields.Selection([('product', 'Product'), ('product_category', 'Product Category')], string='Type', required=True, default='product',
                                 help='Does this rule affects products, or a category of products?')
    product_category_id = fields.Many2one('product.category', string='Category', help='The Product category affected by the rule')
    product_id = fields.Many2one('product.product', string='Target Product', help='The product affected by the rule')
    cumulative = fields.Boolean(help="The points won from this rule will be won in addition to other rules of the same type.\n"
                                "For example, the Program A has three rules applied to the same Product A.\n"
                                " - If the first rule is marked as Cumulative while non the of rest is marked as"
                                " Cumulative, only the first and the second rules will be considered when computing"
                                " won points selling the Product A.\n"
                                " - If the first rule and the second rules are marked as Cumulative, no matter if"
                                " the third one is marked, all those 3 rules will be considered when compute won"
                                " points selling the Product A.\n"
                                " - But if the first rule is NOT marked as Cumulative, it will be the only one that will be"
                                " considered during computing won selling the Product A, no matter if others are marked or not.")
    pp_product = fields.Float(string='Points per product', help='How many points the customer will earn per product ordered')
    pp_currency = fields.Float(string='Points per currency', help='How many points the customer will earn per value sold',
                               digits='Loyalty')
        
