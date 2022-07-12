from odoo import models, fields, _
from odoo.exceptions import ValidationError


class WizardConfirmPurchase(models.TransientModel):
    _name = 'wizard.confirm.purchase'
    _inherit = 'abstract.backdate.wizard'
    _description = 'Purchase Order Confirmation Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)
    date = fields.Datetime(string='Confirmation Date', help="Date on which the purchase order is confirmed. Backdate is supported")

    def process(self):
        for r in self:
            # pass launch_confirmation_wizard=False to context so that the action_confirm will not launch the wizard again
            order = r.purchase_order_id.with_context(launch_confirmation_wizard=False, date_approve=r.date)
            if order.state in ['draft', 'sent']:
                order.button_confirm()
            elif order.state == 'to approve':
                order.button_approve()
            else:
                raise ValidationError(_("The order %s must be in the state of either Draft or Sent or To Approve.") % order.name)
