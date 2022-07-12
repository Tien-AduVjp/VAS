from odoo import models, fields


class FleetFuelPrice(models.Model):
    _name = 'fleet.fuel.price'
    _description = "Fleet Fuel Price"
    _inherit = 'mail.thread'
    _order = 'date desc'
    _rec_name = 'date'

    date = fields.Date(string='Date', tracking=True, required=True, default=fields.Date.today)
    price_per_liter = fields.Float(string='Price Per Liter', tracking=True, required=True)

    _sql_constraints = [
        ('date_unique',
         'UNIQUE(date)',
         "You cannot input fuel price more than once per day"),
        ]

    def get_price(self, date):
        result = self.search([('date', '<=', date)], limit=1)
        return result
