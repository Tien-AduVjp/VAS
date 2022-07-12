from odoo import models, fields, api


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Monetary('Unit Price')
    amount = fields.Monetary(compute='_compute_amount', inverse='_inverse_amount', store=True)
    
    _sql_constraints = [
        ('check_quantity',
         'CHECK (quantity > 0)',
         "Quantity of a service must be positive!"),
    ]
    
    @api.depends('price_unit', 'quantity')
    def _compute_amount(self):
        for r in self:
            r.amount = r.quantity * r.price_unit
    
    def _inverse_amount(self):
        for r in self:
            r.price_unit = r.amount / r.quantity
