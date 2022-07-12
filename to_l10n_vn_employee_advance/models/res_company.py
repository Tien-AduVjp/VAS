from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _prepare_employee_advance_journal_data(self):
        self.ensure_one()
        data = super(ResCompany, self)._prepare_employee_advance_journal_data()
        vn_chart_template_id = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if vn_chart_template_id and self.chart_template_id == vn_chart_template_id:
            account_id = self.env['account.account'].search([
                ('company_id', '=', self.id),
                ('code', 'ilike', '141' + '%')], limit=1)
            data.update({
                'default_debit_account_id': account_id.id,
                'default_credit_account_id': account_id.id,
                })
        return data
