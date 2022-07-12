from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cost_deferral_category_id = fields.Many2one('cost.revenue.deferral.category', string='Cost Deferral Category', help="Once specified,"
                                                " Odoo will try to add some default values when this product gets billed by your vendors."
                                                " I.e., analytic account, analytic tags")
    revenue_deferral_category_id = fields.Many2one('cost.revenue.deferral.category', string='Revenue Deferral Category', help="Once specified,"
                                                   " Odoo will try to add some default values when this product gets invoiced to your customers."
                                                   " I.e., analytic account, analytic tags")
