from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', ondelete='restrict',
                                 help="The analytic account that represents this vehicle")

    def _prepare_analytic_account_vals(self, vehicle_analytic_group=None):
        self.ensure_one()
        vehicle_analytic_group = vehicle_analytic_group or self.env.ref('to_fleet_accounting.analytic_group_vehicles')
        return {
            'name': self.display_name,
            'group_id': vehicle_analytic_group.id
            }

    def _generate_analytic_account_if_not_exists(self):
        AnalyticAccount = self.env['account.analytic.account'].sudo()
        vehicle_analytic_group = self.env.ref('to_fleet_accounting.analytic_group_vehicles')
        for r in self.filtered(lambda v: not v.analytic_account_id):
            acc = AnalyticAccount.search([('name', 'ilike', '%' + r.display_name + '%')], limit=1)
            if not acc:
                acc = AnalyticAccount.create(r._prepare_analytic_account_vals(vehicle_analytic_group))
            if not acc.group_id or acc.group_id != vehicle_analytic_group:
                acc.group_id = vehicle_analytic_group.id
            r.analytic_account_id = acc.id
        return True

    def _synch_analytic_account_name(self):
        for r in self:
            r.analytic_account_id.with_context(vehicle_force_change_name=True).name = r.display_name

    @api.model_create_multi
    def create(self, vals_list):
        records = super(FleetVehicle, self).create(vals_list)
        records._generate_analytic_account_if_not_exists()
        return records

    def _write(self, vals):
        res = super(FleetVehicle, self)._write(vals)
        if 'name' in vals:
            self._synch_analytic_account_name()
        return res
