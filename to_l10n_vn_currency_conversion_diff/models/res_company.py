from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _prepare_currency_conversion_journal_data(self):
        self.ensure_one()
        data = super(ResCompany, self)._prepare_currency_conversion_journal_data()
        vn_chart_template_id = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if vn_chart_template_id and self.chart_template_id == vn_chart_template_id:
            debit_account_id = self.env['account.account'].search([
                ('company_id', '=', self.id),
                ('code', 'ilike', '811' + '%')], limit=1)
            credit_account_id = self.env['account.account'].search([
                ('company_id', '=', self.id),
                ('code', 'ilike', '711' + '%')], limit=1)
            if debit_account_id and credit_account_id:
                data.update({
                    'default_debit_account_id': debit_account_id.id,
                    'default_credit_account_id': credit_account_id.id,
                    })
        return data
