from odoo import models, fields, api
from odoo.osv import expression


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'

    approval_id = fields.Many2one(related='overtime_plan_id.approval_id', store=True)

    @api.model
    def _get_cron_recognize_actual_overtime_domain(self):
        domain = super(HrOvertimePlanLine, self)._get_cron_recognize_actual_overtime_domain()
        return expression.AND([
            domain,
            [('overtime_plan_id.state', 'not in', ('refuse', 'cancel', 'draft'))]
            ])
