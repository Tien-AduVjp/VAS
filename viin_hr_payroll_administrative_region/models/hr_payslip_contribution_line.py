from odoo import models


class HrPayslipContributionLine(models.Model):
    _inherit = 'hr.payslip.contribution.line'

    def _calculate_company_contribution(self):
        self.ensure_one()
        contribution = super(HrPayslipContributionLine, self)._calculate_company_contribution()
        # Calculate employee's maximum contribution amount
        max_contribution_company = self.payroll_contrib_history_id.max_contribution_company
        if max_contribution_company > 0.0 and contribution > max_contribution_company:
            contribution = max_contribution_company
        return contribution

    def _calculate_employe_contribution(self):
        self.ensure_one()
        contribution = super(HrPayslipContributionLine, self)._calculate_employe_contribution()
        # Calculate company's maximum contribution amount
        max_contribution_employee = self.payroll_contrib_history_id.max_contribution_employee
        if max_contribution_employee > 0.0 and contribution > max_contribution_employee:
            contribution = max_contribution_employee
        return contribution
