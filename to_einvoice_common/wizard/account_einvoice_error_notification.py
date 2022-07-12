from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountEinvoiceErrorNotification(models.TransientModel):
    _name = 'account.einvoice.error.notification'
    _description = 'E-Invoice Error Notification Wizard'

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    reason = fields.Char(required=True)
    action = fields.Selection([
        ('1', 'Cancel'),
        ('2', 'Adjustment'),
        ('3', 'Replace'),
        ('4', 'Explanation')
    ], required=True, string='Action')

    # TODO: remove this constraint and Add corresponding features in version 14.0
    @api.constrains('action')
    def _constraint_action(self):
        for r in self:
            if r.action in ('3', '4'):
                raise UserError(_("This action has not been integrated in the system. We will update them in later versions"))

    def action_notif_einvoice_error(self):
        for r in self:
            r.with_context(
                reason=r.reason,
                action=r.action
            ).invoice_id._action_notif_einvoice_error()
