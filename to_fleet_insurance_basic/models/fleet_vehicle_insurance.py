from odoo import fields, models, api, _


class FleetVehicleInsurance(models.Model):
    _name = 'fleet.vehicle.insurance'
    _inherit = 'abstract.fleet.insurance'
    _description = "Fleet Vehicle Insurance"

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='restrict',
                                 tracking=True,
                                 readonly=False, states={'confirmed': [('readonly', True)],
                                                         'cancelled': [('readonly', True)],
                                                         'expired': [('readonly', True)]},
                                 help="The vehicle for which this insurance is applied")

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, _("%(insurance_type)s [%(insurance_ref)s] for %(vehicle_name)s from %(date_start)s to %(date_end)s") % {
                'insurance_type': r.fleet_insurance_type_id.name,
                'insurance_ref': r.name,
                'vehicle_name': r.vehicle_id.display_name,
                'date_start': fields.Date.to_string(fields.Datetime.context_timestamp(r, fields.Datetime.from_string(r.date_start))),
                'date_end': fields.Date.to_string(fields.Datetime.context_timestamp(r, fields.Datetime.from_string(r.date_end))),
                }))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('vehicle_id', 'like', '%' + name + '%'), ('fleet_insurance_type_id', 'like', '%' + name + '%'), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def action_confirm(self):
        for r in self:
            if r.vehicle_id.driver_id and r.vehicle_id.driver_id.id not in r.message_follower_ids.ids:
                r.message_subscribe([r.vehicle_id.driver_id.id])
        super(FleetVehicleInsurance, self).action_confirm()

    def expiry_warning(self):
        email_template = self.env.ref('to_fleet_insurance_basic.email_template_fleet_vehicle_insurance_expiry_warning')
        for r in self:
            r.message_post_with_template(email_template.id)

