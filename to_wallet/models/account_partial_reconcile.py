from odoo import models, fields, api


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    wallet = fields.Boolean(string='Wallet', readonly=True, groups="to_wallet.group_wallet_manager",
                            help="This indicates if this reconcile is for wallet related journal items")

    @api.model_create_multi
    def create(self, vals_list):
        wallet = self._context.get('partial_reconcile_wallet', False)
        force_amount = self._context.get('force_amount', False)
        force_debit_amount_currency = self._context.get('force_debit_amount_currency', False)
        force_credit_amount_currency = self._context.get('force_credit_amount_currency', False)
        for vals in vals_list:
            vals['wallet'] = vals.get('wallet', wallet)
            if force_amount:
                vals['amount'] = force_amount
            if force_debit_amount_currency:
                vals['debit_amount_currency'] = force_debit_amount_currency
            if force_credit_amount_currency:
                vals['credit_amount_currency'] = force_credit_amount_currency
        return super(AccountPartialReconcile, self).create(vals_list)
