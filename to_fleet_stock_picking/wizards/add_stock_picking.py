from odoo import fields, models, _
from odoo.exceptions import UserError


class AddStockPicking(models.TransientModel):
    _name = 'add.stock.picking'
    _description = 'Add Stock Picking'

    stock_picking_ids = fields.Many2many('stock.picking', string='Stock Picking', domain=lambda self: self._default_stock_picking_ids_domain())

    def _default_stock_picking_ids_domain(self):
        domain = [
            ('trip_id', '=', False),
            ('fleet_delivery_address_id', '!=', False),
            ('trip_waypoint_id', '=', False),
            ('state', '!=', 'cancel'),
            '|', ('state', '=', 'assigned'), ('ready_for_fleet_picking', '=', True)
        ]
        return domain

    def add_stock_picking(self):
        trip_id = self._context.get('active_id', False)
        if trip_id:
            trip = self.env['fleet.vehicle.trip'].search([('id', '=', trip_id)])
        for r in self:
            if not r.stock_picking_ids:
                raise UserError(_("You must select stock picking to add to trip."))
            trip.stock_picking_ids |= r.stock_picking_ids
        return {'type': 'ir.actions.act_window_close'}
