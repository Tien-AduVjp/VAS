from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    request_ids = fields.One2many('maintenance.request', 'production_id', string='Maintenance Requests')
    maintenance_count = fields.Integer(compute='_compute_maintenance_count', string='Number of maintenance requests')

    @api.depends('request_ids')
    def _compute_maintenance_count(self):
        requests = self.env['maintenance.request'].read_group([('production_id', 'in', self.ids)], ['production_id'], ['production_id'])
        mapped_data = dict([(req['production_id'][0], req['production_id_count']) for req in requests])
        for r in self:
            r.maintenance_count = mapped_data.get(r.id, 0)

    def button_maintenance_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Maintenance Request'),
            'res_model': 'maintenance.request',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_production_id': self.id,},
            'domain': [('production_id', '=', self.id)],
        }

    def action_view_maintenance_request(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance Requests'),
            'res_model': 'maintenance.request',
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,graph,calendar' if self.maintenance_count != 1 else 'form',
            'res_id': '' if self.maintenance_count != 1 else self.request_ids.id,
            'context': {'default_production_id': self.id,},
            'domain': [('production_id', '=', self.id)],
        }
        return action
