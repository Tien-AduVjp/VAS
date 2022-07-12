from odoo import models, _
from odoo.exceptions import UserError


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def unlink(self):
        if not self._context.get('force_delete_transaction', False):
            cannot_delete = self.filtered(lambda tx: tx.payment_id)
            if cannot_delete:
                raise UserError(_('Could not delete the payment transaction %s which was referred by the payment %s') % (cannot_delete[0].reference, cannot_delete[0].payment_id.name))
        return super(PaymentTransaction, self).unlink()
