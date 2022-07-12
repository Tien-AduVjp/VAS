from odoo import models, _
from odoo.exceptions import ValidationError


class AccountPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    def render(self, reference, amount, currency_id, partner_id=False, values=None):
        """
        Override to modify the transaction of the given reference for wallet params.
        Others that extend this just need to implement the method `payment.transaction._get_wallet_vals()`
        """
        if not bool(values):
            values = {}
        transaction = self.env['payment.transaction'].search([('reference', '=', reference), ('currency_id', '=', currency_id)])
        # there should be no chance of multiple transaction here but it's better to test this
        if len(transaction) > 1:
            raise ValidationError(_("Programming error! There were more than one transactions of the same"
                                  " reference '%s' found in the database which are %s. Please let our"
                                  " administrator know about this for fixing this issue as soon as possible.")
                                    % (reference, ", ".join(transaction.mapped('reference')))
                                    )
        elif len(transaction) == 1:
            valid_fields = list(transaction._fields.keys())
            wallet_vals = transaction._get_wallet_vals()
            vals = {}
            for field, val in wallet_vals.items():
                if field in valid_fields:
                    vals[field] = val
            if bool(vals):
                transaction.write(vals)
            values.update(wallet_vals)
        return super(AccountPaymentAcquirer, self).render(reference, amount, currency_id, partner_id, values)
