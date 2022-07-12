from odoo import fields, models


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    def _default_get_stock_input_account_id(self):
        return self.env.company.property_stock_valuation_account_id

    stock_input_account_id = fields.Many2one('account.account',
                                             string='Stock Input Account',
                                             default=_default_get_stock_input_account_id,
                                             domain=[('deprecated', '=', False)], required=True,
                                             help="Accounts are used in the stock re-input action, "
                                             "to support different entries generation method upon asset.\n"
                                             "When no account is set here, the Stock Input Account "
                                             "on Product Category will be used instead.")
