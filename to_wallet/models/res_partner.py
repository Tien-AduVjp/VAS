from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wallet_ids = fields.One2many('wallet', 'partner_id', groups="to_wallet.group_wallet_manager")
    
    def _parepare_wallet_data(self, currency=None):
        self.ensure_one()
        currency = currency or self.currency_id or self.env.company_currency_id
        return {
            'currency_id': currency.id,
            'partner_id': self.commercial_partner_id.id
            }

    def _create_wallet_if_not_exist(self, currency=None):
        """
        Method to create a partner's wallet in the given currency if not exists.

        :param currency: currency record for which the wallet will be generated.
            If no currency is passed, either the partner's currency or the company's currency will be applied
        :return: return the newly created wallet or the existing one if it exists.
        """
        self.ensure_one()
        currency = currency or self.currency_id or self.env.company.currency_id
        wallet = self.commercial_partner_id.wallet_ids.filtered(lambda w: w.currency_id == currency)
        if not wallet:
            wallet = self.env['wallet'].sudo().create(self._parepare_wallet_data(currency))
        return wallet
