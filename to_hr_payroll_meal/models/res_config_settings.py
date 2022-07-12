from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string='Currency', help="Main currency of the company.")
    meal_emp_price = fields.Monetary(string='Employee price', readonly=False, related='company_id.default_meal_emp_price',
                                     help="Meal price unit that employee must pay")
