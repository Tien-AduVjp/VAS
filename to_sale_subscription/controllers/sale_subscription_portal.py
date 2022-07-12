# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal

from ..models.sale_order_line import PERIODS

class SaleSubscription(http.Controller):

    def _get_sale_subscription(self, subscription_id, uuid=''):
        Subscription = request.env['sale.subscription']
        if uuid:
            subscription = Subscription.sudo().browse(subscription_id)
            if uuid != subscription.uuid:
                raise NotFound()
            if request.uid == subscription.partner_id.user_id.id:
                subscription = Subscription.browse(subscription_id)
        else:
            subscription = Subscription.browse(subscription_id)
        return subscription
    

    @http.route(['/my/subscriptions/<int:subscription_id>/',
                 '/my/subscriptions/<int:subscription_id>/<string:uuid>'], type='http', auth="public", website=True)
    def subscriptions(self, subscription_id, uuid='', message='', message_class='', **kw):
        subscription = self._get_sale_subscription(subscription_id, uuid)

        acquirers = request.env['payment.acquirer'].search([
            ('state', 'in', ['enabled', 'test']),
            ('registration_view_template_id', '!=', False),
            ('token_implemented', '=', True)])
        template = subscription.template_id.sudo()
        missing_periods = False
        if subscription.recurring_rule_type != 'weekly':
            rel_period = relativedelta(datetime.datetime.today(), subscription.recurring_next_date)
            missing_periods = getattr(rel_period, PERIODS[subscription.recurring_rule_type]) + 1
        else:
            delta = datetime.date.today() - subscription.recurring_next_date
            missing_periods = delta.days / 7
        dummy, action = request.env['ir.model.data'].get_object_reference('to_sale_subscription', 'sale_subscription_action')
        values = {
            'subscription': subscription,
            'template': template,
            'display_close': subscription.in_progress,
            'is_follower': request.env.user.partner_id.id in subscription.mapped('message_follower_ids.partner_id').ids,
            'close_reasons': request.env['sale.subscription.close.reason'].search([]),
            'missing_periods': missing_periods,
            'acquirers': list(acquirers),
            'payment_mode': template.payment_mode,
            'acc_pm': subscription.payment_token_id,
            'part_pms': subscription.partner_id.payment_token_ids,
            'user': request.env.user,
            'is_salesman': request.env['res.users'].with_user(request.uid).has_group('sales_team.group_sale_salesman'),
            'action': action,
            'message': message,
            'message_class': message_class,
            'change_pm': kw.get('change_pm') != None,
            'pricelist': subscription.pricelist_id.sudo(),
            'submit_class':'btn btn-primary mb8 mt8 float-right',
            'submit_txt':'Pay Subscription',
            'bootstrap_formatting':True,
            'return_url':'/my/subscriptions/' + str(subscription_id) + '/' + str(uuid),
        }

        history = request.session.get('my_subscriptions_history', [])
        values.update(get_records_pager(history, subscription))
        return request.render("to_sale_subscription.subscription", values)

    payment_succes_msg = 'message=Thank you, your payment has been validated.&message_class=alert-success'
    payment_fail_msg = 'message=Payment error, please try again or contact us.&message_class=alert-danger'

    @http.route(['/my/subscriptions/payment/<int:subscription_id>/',
                 '/my/subscriptions/payment/<int:subscription_id>/<string:uuid>'], type='http', auth="public", methods=['POST'], website=True)
    def payment(self, subscription_id, uuid=None, **kw):
        Invoice = request.env['account.move']
        get_param = ''
        
        subscription = self._get_sale_subscription(subscription_id, uuid)

        # no change
        if int(kw.get('pm_id', 0)) > 0:
            subscription.payment_token_id = int(kw['pm_id'])

        # if no payment has been selected for this subscription, then we display redirect to /my/subscriptions with an error message
        if len(subscription.payment_token_id) == 0:
            get_param = 'message=Please select payment method for this subsription.&message_class=alert-danger'
            return request.redirect('/my/subscriptions/%s/%s?%s' % (subscription.id, subscription.uuid, get_param))

        # we can't call _recurring_invoice because we'd miss 3DS, redoing the whole payment here
        payment_token = subscription.payment_token_id
        if payment_token:
            new_invoice = Invoice.sudo().create(subscription.sudo()._prepare_invoice_data())
            new_invoice.compute_taxes()
            tx = subscription.sudo()._do_payment(payment_token, new_invoice)[0]
            if tx.html_3ds:
                return tx.html_3ds
            get_param = self.payment_succes_msg if tx.state in ['done', 'authorized'] else self.payment_fail_msg
            if tx.state in ['done', 'authorized']:
                subscription.send_success_mail(tx, new_invoice)
                msg_body = 'Manual payment succeeded. Payment reference: <a href=# data-oe-model=payment.transaction data-oe-id=%d>%s</a>; Amount: %s. Invoice <a href=# data-oe-model=account.move data-oe-id=%d>View Invoice</a>.' % (tx.id, tx.reference, tx.amount, new_invoice.id)
                subscription.message_post(body=msg_body)
            else:
                new_invoice.unlink()

        return request.redirect('/my/subscriptions/%s/%s?%s' % (subscription.id, subscription.uuid, get_param))

    # 3DS controllers
    # transaction began as s2s but we receive a form reply
    @http.route(['/my/subscriptions/<sub_uuid>/payment/<int:tx_id>/accept/',
                 '/my/subscriptions/<sub_uuid>/payment/<int:tx_id>/decline/',
                 '/my/subscriptions/<sub_uuid>/payment/<int:tx_id>/exception/'], type='http', auth="public", website=True)
    def payment_accept(self, sub_uuid, tx_id, **kw):
        Subscription = request.env['sale.subscription']

        subscription = Subscription.sudo().search([('uuid', '=', sub_uuid)])
        tx = request.env['payment.transaction'].sudo().browse(tx_id)

        tx.form_feedback(kw, tx.acquirer_id.provider)

        get_param = self.payment_succes_msg if tx.state in ['done', 'authorized'] else self.payment_fail_msg

        return request.redirect('/my/subscriptions/%s/%s?%s' % (subscription.id, sub_uuid, get_param))

    @http.route(['/my/subscriptions/<int:subscription_id>/close'], type='http', methods=["POST"], auth="public", website=True)
    def close_subscription(self, subscription_id, uuid=None, **kw):
        subscription = self._get_sale_subscription(subscription_id, uuid)

        close_reason = request.env['sale.subscription.close.reason'].browse(int(kw.get('close_reason_id')))
        subscription.close_reason_id = close_reason
        if kw.get('closing_reason'):
            subscription.message_post(body=_("The reason for cancelling customer's subscription : ") + kw.get('closing_reason'))
        subscription.action_set_close()
        subscription.date_end = datetime.date.today().strftime('%Y-%m-%d')
        return request.redirect('/my/home')

    @http.route(['/my/subscriptions/<int:subscription_id>/set_pm',
                '/my/subscriptions/<int:subscription_id>/<string:uuid>/set_pm'], type='http', methods=["POST"], auth="public", website=True)
    def set_payment_method(self, subscription_id, uuid=None, **kw):
        subscription = self._get_sale_subscription(subscription_id, uuid)
        message = False
        if kw.get('pm_id'):
            new_token = request.env['payment.token'].browse(int(kw.get('pm_id')))

            if new_token.verified:
                subscription.payment_token_id = new_token
                message = 'message=Payment method for this subscription changed successfully.&message_class=alert-success'
            else:
                message = 'message=Payment method verify successfully. You can use it on a subscription.&message_class=alert-danger'
        else:
            message = 'message=Cannot change your payment method for this subscription.&message_class=alert-danger'

        return request.redirect('/my/subscriptions/%s/%s?%s' % (subscription.id, subscription.uuid, message))
