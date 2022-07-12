from odoo import fields, models, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    request_ids = fields.One2many('maintenance.request', 'workorder_id', string='Maintenance Requests')
    maintenance_request_count = fields.Integer(string='Maintenance Request Count', compute='_compute_maintenance_request')

    def _compute_maintenance_request(self):
        requests = self.env['maintenance.request'].read_group([('workorder_id', 'in', self.ids)], ['workorder_id'], ['workorder_id'])
        mapped_data = dict([(req['workorder_id'][0], req['workorder_id_count']) for req in requests])
        for r in self:
            r.maintenance_request_count = mapped_data.get(r.id, 0)

    def open_maintenance_request_wo(self):
        self.ensure_one()
        action = {
            'name': _('Maintenance Requests'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,graph,calendar',
            'res_model': 'maintenance.request',
            'type': 'ir.actions.act_window',
            'context': {'default_workorder_id': self.id,},
            'domain': [('workorder_id', '=', self.id)],
        }
        if self.maintenance_request_count == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.request_ids.id
        return action


    def button_maintenance_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('New Maintenance Request'),
            'res_model': 'maintenance.request',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {
                'default_production_id': self.production_id.id,
                'default_workorder_id': self.id
                },
            'domain': [('workorder_id', '=', self.id)]
        }
