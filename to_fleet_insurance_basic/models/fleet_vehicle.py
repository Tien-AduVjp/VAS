from odoo import fields, models, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    insurance_ids = fields.One2many('fleet.vehicle.insurance', 'vehicle_id', string='Insurances')
    current_insurance_ids = fields.One2many('fleet.vehicle.insurance', 'vehicle_id', string='Current Insurances', domain=[('state', '=', 'confirmed')])
    current_insurances_count = fields.Integer(string='Current Insurances Count', compute='_compute_current_insurances_count', store=True)

    @api.depends('insurance_ids', 'insurance_ids.state')
    def _compute_current_insurances_count(self):
        for r in self:
            r.current_insurances_count = len(r.insurance_ids.filtered(lambda ins: ins.state == 'confirmed'))

    def action_view_insurances(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_fleet_insurance_basic.action_fleet_vehicle_insurance')

        # reset context
        action['context'] = {'search_default_confirmed':1}
        # choose the view_mode accordingly
        if self.current_insurances_count != 1:
            action['domain'] = "[('id', 'in', " + str(self.insurance_ids.ids) + ")]"
        elif self.current_insurances_count == 1:
            res = self.env.ref('to_fleet_insurance_basic.fleet_vehicle_insurance_form_view', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.current_insurance_ids.id
        return action
