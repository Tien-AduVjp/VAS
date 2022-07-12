from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    currency_conversion_diff_journal_id = fields.Many2one('account.journal', string='Currency Conversion Difference Journal', domain=[('type', '=', 'general')])

    # TODO: rename `income_currency_conversion_diff_account_id` into `currency_conversion_diff_income_account_id`
    income_currency_conversion_diff_account_id = fields.Many2one(
        'account.account',
        readonly=False,
        string="Gain Currency Conversion Account",
        domain="[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id)]",
        help="An account to record gained amount due to currency conversion during online payment transactions. It is usually an Other Income account."
        )
    # TODO: rename `expense_currency_conversion_diff_account_id` into `currency_conversion_diff_expense_account_id`
    expense_currency_conversion_diff_account_id = fields.Many2one(
        'account.account',
        readonly=False,
        string='Loss Currency Conversion Account',
        domain="[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id)]",
        help="An account to record amount lost due to currency conversion during online payment transactions. It is usually an Other Expense account."
        )

    def _prepare_currency_conversion_journal_data(self):
        return {
            'name': _('Currency Conversion Difference'),
            'code': 'CCDJ',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
        }

    def _get_currency_conversion_diff_accounts(self):
        """
        Hook method for other modules to extend for localization
        """
        income_account = self.env['account.account']
        expense_account = self.env['account.account']
        return income_account, expense_account
