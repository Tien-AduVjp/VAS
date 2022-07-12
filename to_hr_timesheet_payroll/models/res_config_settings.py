from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    general_overhead = fields.Float(related='company_id.general_overhead', readonly=False)

    def action_update_employee_timesheet_cost_from_payslips(self):
        self.company_id._update_employee_timesheet_cost_from_payslips()
