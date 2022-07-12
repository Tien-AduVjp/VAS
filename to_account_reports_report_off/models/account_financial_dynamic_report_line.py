from odoo import models


class AccountFinancialDynamicReportLine(models.Model):
    _inherit = "account.financial.dynamic.report.line"

    def _prepare_legal_report_off_domain(self):
        domain = super(AccountFinancialDynamicReportLine, self)._prepare_legal_report_off_domain()
        if self._context['ignored'] == 'hide_ignored':
            domain.append(('legal_report_off', '=', False))
        return domain
