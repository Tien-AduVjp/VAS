from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    meal_emp_price = fields.Float(string="Employee price", readonly=False, related='company_id.default_meal_emp_price', digits='Payroll', help="Meal price unit that employee must pay", default=0)