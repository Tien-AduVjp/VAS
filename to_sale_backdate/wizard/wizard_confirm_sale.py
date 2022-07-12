from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WizardConfirmSale(models.TransientModel):
    _name = 'wizard.confirm.sale'
    _description = 'Sales Order Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True, ondelete='cascade')
    confirmation_date = fields.Datetime(string='Confirmation Date', default=fields.Datetime.now,
                                        help="Date on which the sales order is confirmed. Backdate is supported")

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
                r.sale_order_id.with_context(date_order=r.confirmation_date, launch_confirmation_wizard=False).action_confirm()
            else:
                r.sale_order_id.with_context(launch_confirmation_wizard=False).action_confirm()
