from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WizardConfirmPurchase(models.TransientModel):
    _name = 'wizard.confirm.purchase'
    _description = 'Purchase Order Confirmation Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    confirmation_date = fields.Datetime(string='Confirmation Date', default=fields.Datetime.now,
                                        help="Date on which the purchase order is confirmed. Backdate is supported")

    @api.constrains('confirmation_date')
    def _validate_confirmation_date(self):
        if self.confirmation_date and self.confirmation_date > fields.Datetime.now():
            raise ValidationError(_("You must not use a future date as the Confirmation Date. You can either leave the"
                                    " field Confirmation Date empty for the current date or enter a date in the past"
                                    " in case you want to do backdate."))

    def action_confirm(self):
        for r in self:
            # pass launch_confirmation_wizard=False to context so that the action_confirm will not launch the wizard again
            if r.confirmation_date:
                order = r.purchase_order_id.with_context(launch_confirmation_wizard=False, date_approve=r.confirmation_date)
            else:
                order = r.purchase_order_id.with_context(launch_confirmation_wizard=False)
            if order.state in ['draft', 'sent']:
                order.button_confirm()
            elif order.state == 'to approve':
                order.button_approve()
            else:
                raise ValidationError(_("The order %s must be in the state of either Draft or Sent or To Approve.") % order.name)
