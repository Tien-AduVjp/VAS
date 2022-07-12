from odoo import models, fields, api, _


class EventEvent(models.Model):
    _inherit = 'event.event'

    total_timesheet_hours = fields.Integer(string='Timesheet Hours', compute='_compute_total_hour', store=True)
    timesheet_encode_uom_id = fields.Many2one('uom.uom', related='company_id.timesheet_encode_uom_id')

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
    @api.depends('company_id.timesheet_encode_uom_id', 'project_ids.timesheet_ids.unit_amount', 'project_ids.timesheet_ids.product_uom_id')
    def _compute_total_hour(self):
        for r in self:
            r.total_timesheet_hours = sum(r.project_ids.mapped('total_timesheet_time'))
