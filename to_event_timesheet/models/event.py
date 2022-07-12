from odoo import models, fields, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    total_hour = fields.Float('Timesheet Hours', compute='_compute_total_hour', store=True)

    def action_timesheet_view(self):
        self.ensure_one()
        ctx = dict(self._context or {})
        ctx.update({'event_id': self.id,})
        tree_view_id = self.env.ref('hr_timesheet.timesheet_view_tree_user').id
        if self.project_ids:
            ctx.update({
                'default_project_id': self.project_ids[0].id,
            })

        return {
            'name': _('Timesheet'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'tree',
            'view_id': tree_view_id,
            'domain': [('project_id', 'in', self.project_ids.ids)],
            'target': 'current',
            'context': ctx,
        }

    @api.depends('project_ids.timesheet_ids', 'project_ids.timesheet_ids.unit_amount')
    def _compute_total_hour(self):
        for r in self:
            r.total_hour = 0.0
            if r.project_ids.timesheet_ids:
                r.total_hour = sum(r.project_ids.timesheet_ids.mapped('unit_amount'))
