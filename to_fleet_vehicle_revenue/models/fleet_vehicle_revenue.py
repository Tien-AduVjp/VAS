from odoo import fields, models, api, _
from odoo.exceptions import UserError


class FleetVehicleRevenue(models.Model):
    _name = 'fleet.vehicle.revenue'
    _description = 'Revenue related to a vehicle'
    _order = 'date desc, vehicle_id asc'

    name = fields.Char(related='vehicle_id.name', string='Name', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, help='Vehicle concerned by this log')
    revenue_subtype_id = fields.Many2one('fleet.service.type', 'Type')
    revenue_type = fields.Selection([('contract', 'Contract'), ('services', 'Services'), ('both', 'Contracts & Services')],
                                    string='Category of the Revenue', related='revenue_subtype_id.category',
                                    readonly=True, store=True, help='For internal purpose only')
    amount = fields.Float('Total Price')
    odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer', help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value', help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)
    date = fields.Date(help='Date when the cost has been executed')
    auto_generated = fields.Boolean('Automatically Generated', readonly=True)

    def _get_odometer(self):
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value
            else:
                record.odometer = 0.0

    def _set_odometer(self):
        for record in self:
            if not record.odometer:
                raise UserError(_('Emptying the odometer value of a vehicle is not allowed.'))
            odometer = self.env['fleet.vehicle.odometer'].create({
                'value': record.odometer,
                'date': record.date or fields.Date.context_today(record),
                'vehicle_id': record.vehicle_id.id
            })
            self.odometer_id = odometer

    @api.model_create_multi
    def create(self, vals_list):
        # make sure that the data are consistent with values of parent and contract records given
        for vals in vals_list:
            if 'odometer' in vals and not vals['odometer']:
                # if received value for odometer is 0, then remove it from the data as it would result to the creation of a
                # odometer log with 0, which is to be avoided
                del(vals['odometer'])
        return super(FleetVehicleRevenue, self).create(vals_list)

