from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_cost_revenue_deferred = fields.Boolean(string='Cost/Revenue Recognition')
    module_to_account_reports = fields.Boolean("Advanced Dynamic Reports")
    module_to_account_asset = fields.Boolean(string='Accounting Assets Management')
    module_to_account_budget = fields.Boolean(string='Budgets Management')
    module_viin_auto_currency_rate = fields.Boolean("Automatic Currency Rates Update")

    @api.onchange('module_to_account_budget')
    def _onchange_module_to_account_budget(self):
        if self.module_to_account_budget:
            self.group_analytic_accounting = True
