from odoo import fields, models


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    amount_double_validation = fields.Monetary(related='company_id.amount_double_validation', readonly=False)
    use_employee_advance_pass_through_account = fields.Boolean(string='Use Pass-Through Account In Employee Advance',
                                                               related='company_id.use_employee_advance_pass_through_account', readonly=False)
