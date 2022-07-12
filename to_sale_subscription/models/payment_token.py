from odoo import models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    def get_linked_records(self):
        """ This method returns a dict containing all the records linked to the payment.token (e.g Subscriptions),
            the key is the id of the payment.token and the value is an array that must follow the scheme below.

            {
                token_id: [
                    'description': The model description (e.g 'Sale Subscription'),
                    'id': The id of the record,
                    'name': The name of the record,
                    'url': The url to access to this record.
                ]
            }
        """
        res = super(PaymentToken, self).get_linked_records()

        subscriptions = self.env['sale.subscription'].search([('payment_token_id', 'in', self.ids)])
        for r in self:
            for s in subscriptions.filtered(lambda s: s.payment_token_id.id == r.id):
                res[r.id].append(s._prepare_payment_token_linked_record_data())
        return res
