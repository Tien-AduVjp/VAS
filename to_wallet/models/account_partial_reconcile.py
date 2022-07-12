from odoo import models, fields, api


class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    wallet = fields.Boolean(string='Wallet', readonly=True, groups="to_wallet.group_wallet_manager",
                            help="This indicates if this reconcile is for wallet related journal items")

    @api.model
    def _prepare_exchange_diff_partial_reconcile(self, aml, line_to_reconcile, currency):
        """
        This override ensures the exchange rate line to reconcile must be a wallet
        move line if the given move line aml is also a wallet one
        """
        if aml.wallet:
            line_to_reconcile.filtered(lambda l: not l.wallet).write({'wallet': True})
        res = super(AccountPartialReconcile, self)._prepare_exchange_diff_partial_reconcile(aml, line_to_reconcile, currency)
        res['wallet'] = line_to_reconcile.wallet
        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        wallet = self._context.get('partial_reconcile_wallet', False)
        force_amount_currency = self._context.get('force_amount_currency', False)
        force_reconcile_currency_id = self._context.get('force_reconcile_currency_id', False) if force_amount_currency else False
        for vals in vals_list:
            vals['wallet'] = vals.get('wallet', wallet)
            if not vals.get('currency_id', False):
                vals['currency_id'] = force_reconcile_currency_id
                if not vals['amount_currency'] and force_amount_currency:
                    vals['amount_currency'] = force_amount_currency
        return super(AccountPartialReconcile, self).create(vals_list)

