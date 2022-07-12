from odoo import fields, models, api


class FleetInsuranceType(models.Model):
    _name = 'fleet.insurance.type'
    _inherit = 'mail.thread'
    _description = 'Fleet Insurance Type'

    name = fields.Char(string='Title', required=True, translate=True, tracking=True)
    period = fields.Integer(string='Insurance Period', required=True, default=12, tracking=True, help="The default period in months for the insurance of this type")
    days_to_notify = fields.Integer(string='Days to notify', default=7, required=True, tracking=True,
                                    help="Number of days prior to the expiry to notify the insurance's followers.")
    vehicle_insurance_ids = fields.One2many('fleet.vehicle.insurance', 'fleet_insurance_type_id',
                                            groups='fleet.fleet_group_user',
                                            string='Vehicle Insurance', help="List of vehicle insurances of this type")
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicles', compute='_compute_vehicle_ids', store=True,
                                   help="The vehicles that currently have active_insurances of this type")
    vehicles_count = fields.Integer(string='Vehicles Count', compute='_compute_vehicles_count', store=True)

    _sql_constraints = [
        ('positive_days_to_notify_check',
         'CHECK(days_to_notify >= 0)',
         "Days to Notify must be greater than or equal to zero!"),
    ]

    @api.depends('vehicle_insurance_ids', 'vehicle_insurance_ids.state', 'vehicle_insurance_ids.vehicle_id')
    def _compute_vehicle_ids(self):
        for r in self:
            r.vehicle_ids = r.vehicle_insurance_ids.filtered(lambda ins: ins.state == 'confirmed').mapped('vehicle_id').ids

    @api.depends('vehicle_ids')
    def _compute_vehicles_count(self):
        for r in self:
            r.vehicles_count = len(r.vehicle_ids)
