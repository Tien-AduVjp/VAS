from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    show_both_dr_and_cr_trial_balance = fields.Boolean(string="Show both debit and credit on Trial Balance", default=False, help="Allow show both debit and credit on Trial Balance")

    @api.model
    def _get_show_both_dr_and_cr_trial_balance_domain(self):
        return []

    @api.model
    def _apply_show_both_dr_and_cr_trial_balance(self):
        domain = self._get_show_both_dr_and_cr_trial_balance_domain()
        if domain:
            accounts = self.env['account.account'].sudo().search(domain)
            if accounts:
                accounts.sudo().write({'show_both_dr_and_cr_trial_balance': True})
