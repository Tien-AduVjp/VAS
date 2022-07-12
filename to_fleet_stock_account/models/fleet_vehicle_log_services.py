from odoo import models, api

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    def _is_invoiceable(self):
        return super(FleetVehicleLogServices, self)._is_invoiceable() and not self.created_from_stock_move_id

    @api.depends('created_from_stock_move_id')
    def _compute_invoiceable(self):
        super(FleetVehicleLogServices, self)._compute_invoiceable()
