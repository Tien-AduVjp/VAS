from odoo import fields, models

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    pos_category_id = fields.Many2one('pos.category', string='Pos Category', help='The Pos category affected by the rule')
    rule_type = fields.Selection(selection_add=[('pos_category', 'Pos Category')], ondelete={'pos_category': 'cascade'})

