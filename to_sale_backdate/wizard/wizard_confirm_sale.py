from odoo import models, fields


class WizardConfirmSale(models.TransientModel):
    _name = 'wizard.confirm.sale'
    _inherit = 'abstract.backdate.wizard'
    _description = 'Sales Order Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', required=True, ondelete='cascade')
    date = fields.Datetime(string='Confirmation Date', help="Date on which the sales order is confirmed. Backdate is supported")

    def process(self):
        self.ensure_one()
        # pass launch_confirmation_wizard=False to context so that the action_confirm will not launch the wizard again
        self.sale_order_id.with_context(date_order=self.date, launch_confirmation_wizard=False).action_confirm()
