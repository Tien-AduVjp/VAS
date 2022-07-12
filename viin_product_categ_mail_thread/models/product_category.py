from odoo import fields, models


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'mail.thread']

    name = fields.Char(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    property_account_income_categ_id = fields.Many2one(tracking=True)
    property_account_expense_categ_id = fields.Many2one(tracking=True)
