from odoo import models, api, fields


class HrPayrollContribActionSuspend(models.TransientModel):
    _name = 'hr.payroll.contrib.action.suspend'
    _inherit = 'abstract.hr.payroll.contrib.act'
    _description = "Payroll Contribution Action Suspend"
    
    payroll_contribution_reg_ids = fields.Many2many('hr.payroll.contribution.register', relation='wizard_action_suspend_payroll_contrib_rel', string='Payroll Contribution Register', required=True)

    def process(self):
        self.ensure_one()
        self.payroll_contribution_reg_ids.write({'date_suspended':self.date})
        self.payroll_contribution_reg_ids.with_context(call_wizard=False).action_suspend()
