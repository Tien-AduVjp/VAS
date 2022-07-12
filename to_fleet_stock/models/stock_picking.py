from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_service_type_id = fields.Many2one('fleet.service.type', string='Vehicle Service',
                                            states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                            help="A service type of the fleet related to this stock picking. E.g."
                                            " part replacement, refueling, etc.")
    def action_confirm(self):
        for r in self.filtered(lambda r: r.picking_type_code == 'fleet_consumption'):
            if r.move_lines:
                if r.fleet_service_type_id:
                    if any(not l.vehicle_id for l in r.move_lines):
                        raise ValidationError(_("You have selected a fleet service for the picking while you have not"
                                                " specified a vehicle for all the move lines in the Initial Demand tab."))
                else:
                    if any(l.vehicle_id for l in r.move_lines):
                        raise ValidationError(_("You have input a vehicle in a move line in the Initial Demand tab but"
                                                " you have not specified a vehicle service for the picking."))
        return super(StockPicking, self).action_confirm()
