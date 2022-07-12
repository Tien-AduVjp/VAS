from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_stock_account_input_categ_id = fields.Many2one(tracking=True)
    property_stock_account_output_categ_id = fields.Many2one(tracking=True)
    property_stock_valuation_account_id = fields.Many2one(tracking=True)
    property_stock_journal = fields.Many2one(tracking=True)
    property_cost_method = fields.Selection(tracking=True)
    property_valuation = fields.Selection(tracking=True)
    removal_strategy_id = fields.Many2one(tracking=True)
