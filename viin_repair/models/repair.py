from odoo import fields, models, api


class Repair(models.Model):
    _inherit = 'repair.order'

    repair_date = fields.Date(string='Repair date', default=fields.Date.today)
    feedback = fields.Text("Customer's Feedback")
    forecast = fields.Text("Forecast")

    @api.onchange('lot_id')
    def _onchange_location_id(self):
        if self.state == 'draft':
            if self.lot_id.customer_id:
                self.partner_id = self.lot_id.customer_id
            else:
                self.partner_id = False
