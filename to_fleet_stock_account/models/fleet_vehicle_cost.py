from odoo import models, api

class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    def _is_invoiceable(self):
        return super(FleetVehicleCost, self)._is_invoiceable() and not self.created_from_stock_move_id

    @api.depends('created_from_stock_move_id')
    def _compute_invoiceable(self):
        super(FleetVehicleCost, self)._compute_invoiceable()
