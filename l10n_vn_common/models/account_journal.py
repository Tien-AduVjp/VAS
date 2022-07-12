from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    suspense_account_id = fields.Many2one(help="Bank/Cash statements transactions will be posted on the suspense account until the final reconciliation "
             "allowing finding the right account.", string='Suspense Account')

    def _compute_suspense_account_id(self):
        super(AccountJournal, self)._compute_suspense_account_id()
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        for r in self.filtered(
            lambda jnr: jnr.company_id.chart_template_id.id in vn_charts.ids \
            and jnr.type == 'cash' \
            and not jnr._origin.suspense_account_id
            ):
            r.suspense_account_id = r.company_id.account_journal_cash_suspense_account_id

    @api.model
    def _prepare_liquidity_account_vals(self, company, code, vals):
        # OVERRIDE
        account_vals = super()._prepare_liquidity_account_vals(company, code, vals)

        if company.country_id.code == 'VN':
            # Ensure the newly liquidity accounts have the right account tag in order to be part
            # of the Vietnam financial reports.
            account_vals.setdefault('tag_ids', [])
            if code.startswith('111'):
                account_vals['tag_ids'].append((4, self.env.ref('l10n_vn_common.account_account_tag_111').id))
            else:
                account_vals['tag_ids'].append((4, self.env.ref('l10n_vn_common.account_account_tag_112').id))

        return account_vals

    @api.model
    def _fill_missing_values(self, vals):
        journal_type = vals.get('type')
        if not journal_type:
            return
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        company = self.env['res.company'].browse([vals['company_id']]) if vals.get('company_id') else self.env.company
        if company.chart_template_id.id in vn_charts.ids and journal_type in ('bank', 'cash'):
            # We are about to call super that would create accounts for `payment_debit_account_id`
            # and payment_credit_account_id if their evaluation is False.
            # In order to avoid such creation that we don't want, put any negative value here to avoid
            # False valuation later during super call execution
            vals.update({
                'payment_debit_account_id': -10,
                'payment_credit_account_id': -10
            })

        super(AccountJournal, self)._fill_missing_values(vals)

        if company.chart_template_id.id in vn_charts.ids and journal_type in ('bank', 'cash'):
            random_account = self.env['account.account'].search([('company_id', '=', company.id)], limit=1)
            digits = len(random_account.code) if random_account else 6
            current_assets_type = self.env.ref('account.data_account_type_current_assets')
            if journal_type == 'bank':
                liquidity_account_prefix = company.bank_account_code_prefix or ''
            else:
                liquidity_account_prefix = company.cash_account_code_prefix or company.bank_account_code_prefix or ''
            default_account_code = self.env['account.account'].browse([vals['default_account_id']]).code
            vals['payment_debit_account_id'] = self.env['account.account'].create({
                'name': _("Outstanding Receipts (%s)") % (vals['name']),
                'code': self.env['account.account'].with_context({
                    'default_account_code': default_account_code
                })._search_new_account_code(company, digits, liquidity_account_prefix),
                'reconcile': True,
                'user_type_id': current_assets_type.id,
                'company_id': company.id,
            }).id
            vals['payment_credit_account_id'] = self.env['account.account'].create({
                'name': _("Outstanding Payments (%s)") % (vals['name']),
                'code': self.env['account.account'].with_context({
                    'default_account_code': default_account_code
                })._search_new_account_code(company, digits, liquidity_account_prefix),
                'reconcile': True,
                'user_type_id': current_assets_type.id,
                'company_id': company.id,
            }).id
