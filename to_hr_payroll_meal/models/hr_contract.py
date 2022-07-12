from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    pay_per_meal = fields.Monetary('Pay Per Meal', default=lambda self: self.env.company.default_meal_emp_price or 0.0,
                                help="The amount that the employee has to pay when place meal orders and will be"
                                " deducted from the payslips of this employee according to the number of ordered"
                                " meals accordingly.")
