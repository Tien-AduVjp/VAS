from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.http import request


class WalletPortal(CustomerPortal):

    @property
    def _partner_sudo(self):
        return request.env.user.partner_id.sudo()

    @property
    def _wallets(self):
        return self._partner_sudo.commercial_partner_id.wallet_ids

    def _prepare_home_portal_values(self, counters):
        value = super(WalletPortal, self)._prepare_home_portal_values(counters)
        if 'wallet_count' in counters:
            value['wallet_count'] = len(self._wallets)
        return value

    def _prepare_wallets_page_values(self):
        return {
            'page_name': 'wallets',
            'default_url': '/my/wallets',
            'wallets': self._wallets,
            'partner_id': self._partner_sudo.id
        }

    @http.route('/my/wallets', type='http', auth='user', website=True)
    def wallets_page(self, **kwargs):
        values = self._prepare_wallets_page_values()
        return request.render('to_wallet.portal_wallets_page', values)

    def _prepapre_wallet_payment_page_values(self, wallet):
        values = dict(
            wallet=wallet,
            acquirers=wallet.get_payment_acquirers()
        )
        return values

    def _get_wallet_by_id(self, id):
        return self._wallets.filtered(lambda w: w.id == id)

    @http.route('/my/wallet/<int:wallet_id>/payment', type='http', auth='user', website=True)
    def wallet_payment_page(self, wallet_id, **kwargs):
        wallet = self._get_wallet_by_id(wallet_id)
        if wallet:
            values = self._prepapre_wallet_payment_page_values(wallet)
            return request.render('to_wallet.portal_wallet_payment_page', values)
        return request.redirect('/my/wallets')

    @http.route('/my/wallet/<int:wallet_id>/transaction', type='json', auth='user', website=True)
    def wallet_payment_transaction(self, wallet_id, acquirer_id, **kwargs):
        wallet = self._get_wallet_by_id(wallet_id)
        if not wallet:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except:
            return False

        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        if not acquirer.exists():
            return False

        amount = float(request.httprequest.args.get('amount', 0.0))
        if not amount:
            return False

        return_url = '/my/wallet/{}/transaction-status'.format(wallet.id)
        transaction = wallet.sudo().create_payment_transaction(acquirer, amount, return_url=return_url)
        PaymentProcessing.add_payment_transaction(transaction)
        return transaction.render_wallet_payment_form()

    @http.route('/my/wallet/<int:wallet_id>/transaction-status', type='http', auth='user', website=True)
    def wallet_transaction_status(self, wallet_id):
        wallet = self._get_wallet_by_id(wallet_id)
        if not wallet:
            return request.redirect('/my/wallets')

        transaction = wallet.get_last_transaction()
        if not transaction:
            return request.redirect('/my/wallets')

        PaymentProcessing.remove_payment_transaction(transaction)

        values = {
            'wallet': wallet,
            'transaction': transaction
        }
        return request.render('to_wallet.portal_wallet_transaction_status_page', values)
