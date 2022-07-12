from odoo import models, _


class AbstractQualityMrp(models.AbstractModel):
    _name = 'abstract.quality.mrp'
    _description = 'Abstract Quality MRP'
    
    def _compute_check_todo(self, field):
        field_count = field + '_count'
        checks = self.env['quality.check'].read_group([(field, 'in', self.ids), ('quality_state', '=', 'none')], [field], [field])
        mapped_data = dict([(c[field][0], c[field_count]) for c in checks])
        for r in self:
            if mapped_data.get(r.id, False):
                r.check_todo = True
            else:
                r.check_todo = False

    def _compute_alert_count(self, field):
        field_count = field + '_count'
        alert_data = self.env['quality.alert'].read_group([(field, 'in', self.ids)], [field], [field])
        mapped_data = {}
        for d in alert_data:
            mapped_data[d[field][0]] = d[field_count] 
        for r in self:
            r.alert_count = mapped_data.get(r.id, 0)

    def action_view_quality_alerts_mo(self, field):
        self.ensure_one()
        if self.alert_count != 1:
            action_quality_alert = self.env.ref('to_quality.quality_alert_action_check')
            if action_quality_alert:
                action = action_quality_alert.read([])[0]
                action['domain'] = [(field, '=', self.id)]
                action['context'] = {'default_production_id': self.id}
                return action
        else:
            res_id = self.env['quality.alert'].search([(field, '=', self.id)])
            view = self.env.ref('to_quality.quality_alert_view_form')
            return {
                'name': _('Quality Alerts'),
                'type': 'ir.actions.act_window',
                'res_model': 'quality.alert',
                'context': {field: self.ids},
                'res_id': res_id.id,
                'views': [(view.id, 'form')],
            }

    def action_view_quality_alerts(self):
        self.ensure_one()
        context = self.env.context
        eid = context.get('eid', False)
        action_quality_alert = self.env.ref(eid)
        if action_quality_alert:
            action = action_quality_alert.read([])[0]
            action['context'] = context
            action['views'] = [(view_id, mode) for (view_id, mode) in action['views'] if mode == 'form'] or action['views']
            return action

    def check_quality(self):
        self.ensure_one()
        checks = self.check_ids.filtered(lambda x: x.quality_state == 'none')
        if checks:
            action_quality_check = self.env.ref('to_quality.quality_check_action_small')
            if action_quality_check:
                action = action_quality_check.read([])[0]
                action['context'] = self.env.context
                action['res_id'] = checks[0].id
                return action
